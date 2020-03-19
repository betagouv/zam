"""
NB: make sure tasks.huey.init_huey() has been called before importing this module
"""
import logging
from typing import Optional

import transaction

from zam_repondeur.models import Chambre, DBSession, Dossier, Lecture, Texte, User
from zam_repondeur.models.events.dossier import LecturesRecuperees
from zam_repondeur.models.events.lecture import (
    AmendementsAJour,
    AmendementsNonRecuperes,
    AmendementsNonTrouves,
    AmendementsRecuperes,
    ArticlesRecuperes,
    LectureCreee,
    TexteMisAJour,
)
from zam_repondeur.services.data import repository
from zam_repondeur.services.fetch import get_articles
from zam_repondeur.services.fetch.amendements import FetchResult, RemoteSource
from zam_repondeur.services.fetch.an.dossiers.models import DossierRef, LectureRef
from zam_repondeur.services.fetch.senat.scraping import create_dossier_ref
from zam_repondeur.tasks.huey import huey
from zam_repondeur.utils import Timer

logger = logging.getLogger(__name__)


RETRY_DELAY = 5 * 60  # 5 minutes


@huey.task(retries=3, retry_delay=RETRY_DELAY)
def update_dossier(dossier_pk: int, force: bool = False) -> None:
    with huey.lock_task(f"dossier-{dossier_pk}"):
        dossier = DBSession.query(Dossier).get(dossier_pk)
        if dossier is None:
            logger.error(f"Dossier {dossier_pk} introuvable")
            return

        # First fetch data from existing lectures, starting with recents.
        for lecture in reversed(dossier.lectures):

            # Auto fetch articles only for recent lectures.
            if force or lecture.refreshable_for("articles", huey.settings):
                fetch_articles(lecture.pk)

            # Only fetch amendements for recent lectures.
            if force or lecture.refreshable_for("amendements", huey.settings):
                fetch_amendements(lecture.pk)

        # Then try to create missing lectures.
        create_missing_lectures(dossier.pk)


@huey.task(retries=3, retry_delay=RETRY_DELAY)
def fetch_articles(lecture_pk: Optional[int]) -> bool:
    if lecture_pk is None:
        logger.error(f"fetch_articles: lecture_pk is None")
        return False

    with huey.lock_task(f"lecture-{lecture_pk}"):
        lecture = DBSession.query(Lecture).with_for_update().get(lecture_pk)
        if lecture is None:
            logger.error(f"Lecture {lecture_pk} introuvable")
            return False

        changed: bool = get_articles(lecture)
        if changed:
            ArticlesRecuperes.create(lecture=lecture)
        return changed


@huey.task(retries=3, retry_delay=RETRY_DELAY)
def fetch_amendements(lecture_pk: Optional[int]) -> bool:
    if lecture_pk is None:
        logger.error(f"fetch_amendements: lecture_pk is None")
        return False

    with huey.lock_task(f"lecture-{lecture_pk}"):

        lecture = DBSession.query(Lecture).get(lecture_pk)
        if lecture is None:
            logger.error(f"Lecture {lecture_pk} introuvable")
            return False

        total_timer = Timer()
        total_timer.start()

        # This allows disabling the prefetching in tests.
        prefetching_enabled = int(huey.settings["zam.http_cache_duration"]) > 0

        source = RemoteSource.get_remote_source_for_chambre(
            chambre=lecture.chambre,
            settings=huey.settings,
            prefetching_enabled=prefetching_enabled,
        )
        if source is None:
            return False

        logger.info("Récupération des amendements de %r", lecture)

        # Allow prefetching of URLs into the requests cached session.
        with Timer() as prepare_timer:
            source.prepare(lecture)
        logger.info("Time to prepare: %.1fs", prepare_timer.elapsed())

        cumulated_result = FetchResult.create()

        nb_batches = 1
        start_index = 0

        while True:

            logger.info("Starting to collect batch #%d", nb_batches)

            # Collect data about new and updated amendements.
            with Timer() as collect_timer:
                changes = source.collect_changes(
                    lecture=lecture, start_index=start_index
                )
            logger.info("Time to collect batch: %.1fs", collect_timer.elapsed())

            # Then apply the actual changes in a fresh transaction, in order to minimize
            # the duration of database locks (if we hold locks too long, we could have
            # synchronization issues with the webapp, causing unwanted delays for users
            # on some interactive operations).

            # But during tests we want everything to run in a single transaction that
            # we can roll back at the end.
            if not huey.immediate:
                transaction.commit()
                transaction.abort()
                transaction.begin()

            lecture = DBSession.query(Lecture).with_for_update().get(lecture_pk)
            if lecture is None:
                logger.error(f"Lecture {lecture_pk} introuvable")
                return False

            with Timer() as apply_timer:
                batch_result = source.apply_changes(lecture, changes)
            logger.info("Time to apply batch: %.1fs", apply_timer.elapsed())

            logger.info(
                "Total batch time: %.1fs",
                sum(t.elapsed() for t in (prepare_timer, collect_timer, apply_timer)),
            )

            if batch_result.created:
                AmendementsRecuperes.create(
                    lecture=lecture, count=len(batch_result.created)
                )

            if batch_result.errored:
                AmendementsNonRecuperes.create(
                    lecture=lecture,
                    missings=[str(num) for num in sorted(batch_result.errored)],
                )

            cumulated_result += batch_result
            if batch_result.next_start_index is None:
                break

            start_index = batch_result.next_start_index

            nb_batches += 1

        total_timer.stop()
        logger.info(
            "Total time for %d batches: %.1fs", nb_batches, total_timer.elapsed()
        )

        if not cumulated_result.fetched:
            AmendementsNonTrouves.create(lecture=lecture)

        if cumulated_result.changed:
            AmendementsAJour.create(lecture=lecture)

        return cumulated_result.changed


@huey.task()
def create_missing_lectures(dossier_pk: int, user_pk: Optional[int] = None) -> None:
    with huey.lock_task(f"dossier-{dossier_pk}"):
        dossier = DBSession.query(Dossier).get(dossier_pk)
        if dossier is None:
            logger.error(f"Dossier {dossier_pk} introuvable")
            return

        if dossier.an_id.startswith("dummy-"):  # FIXME: just a quick hack
            return

        if user_pk is not None:
            user = DBSession.query(User).get(user_pk)
        else:
            user = None

        changed = False
        changed |= create_missing_lectures_an(dossier, user)
        changed |= create_missing_lectures_senat(dossier, user)

        if changed:
            LecturesRecuperees.create(dossier=dossier, user=user)


def create_missing_lectures_an(dossier: Dossier, user: Optional[User]) -> bool:
    # FIXME: error handling

    dossier_ref_an: Optional[DossierRef]

    if dossier.an_id:
        dossier_ref_an = repository.get_opendata_dossier_ref(dossier.an_id)
    else:
        dossier_ref_senat = repository.get_senat_scraping_dossier_ref(dossier.senat_id)
        dossier_ref_an = find_matching_dossier_ref_an(dossier_ref_senat)

    changed = False
    if dossier_ref_an:
        for lecture_ref in dossier_ref_an.lectures:
            if lecture_ref.chambre == Chambre.AN:
                changed |= create_or_update_lecture(dossier, lecture_ref, user)
    return changed


def find_matching_dossier_ref_an(dossier_ref_senat: DossierRef) -> Optional[DossierRef]:
    # The Sénat dossier_ref usually includes the AN webpage URL, so we try to find
    # an indexed AN dossier_ref with the same AN URL
    an_url = dossier_ref_senat.normalized_an_url
    if an_url:
        dossier_ref = repository.get_opendata_dossier_ref_by_an_url(an_url)
        if dossier_ref:
            return dossier_ref

    # As a fallback, try to find an indexed AN dossier_ref with the same Sénat URL
    senat_url = dossier_ref_senat.normalized_senat_url
    if senat_url:
        dossier_ref = repository.get_opendata_dossier_ref_by_senat_url(senat_url)
        if dossier_ref:
            return dossier_ref

    return None


def create_missing_lectures_senat(dossier: Dossier, user: Optional[User]) -> bool:
    dossier_ref_senat: Optional[DossierRef]

    if dossier.senat_id:
        dossier_ref_senat = get_senat_dossier_ref_from_cache_or_scrape(
            dossier_id=dossier.senat_id
        )
    else:
        dossier_ref_an = repository.get_opendata_dossier_ref(dossier.an_id)
        dossier_ref_senat = find_matching_dossier_ref_senat(dossier_ref_an)

    changed = False
    if dossier_ref_senat is not None:
        for lecture_ref in dossier_ref_senat.lectures:
            if lecture_ref.chambre == Chambre.SENAT:
                changed |= create_or_update_lecture(dossier, lecture_ref, user)
    return changed


def find_matching_dossier_ref_senat(dossier_ref_an: DossierRef) -> Optional[DossierRef]:
    # The AN dossier_ref usually includes the Sénat webpage URL, so we try this first
    senat_url = dossier_ref_an.senat_url
    dossier_id = dossier_ref_an.senat_dossier_id
    if senat_url and dossier_id:
        return get_senat_dossier_ref_from_cache_or_scrape(dossier_id=dossier_id)

    # As a fall back, we index the Sénat dossier_refs by AN webpage URL, so if
    # the information is available in that direction, we can still find it
    an_url = dossier_ref_an.normalized_an_url
    return repository.get_senat_scraping_dossier_ref_by_an_url(an_url)


def get_senat_dossier_ref_from_cache_or_scrape(dossier_id: str) -> DossierRef:
    """
    Get dossier from the Redis cache (if recent) or scrape it
    """
    dossier_ref_senat = repository.get_senat_scraping_dossier_ref(dossier_id)
    if dossier_ref_senat is None:
        dossier_ref_senat = create_dossier_ref(dossier_id)
    return dossier_ref_senat


def create_or_update_lecture(
    dossier: Dossier, lecture_ref: LectureRef, user: Optional[User]
) -> bool:
    changed = False

    lecture_created = False
    lecture_updated = False

    texte = Texte.get_or_create_from_ref(lecture_ref.texte, lecture_ref.chambre)

    lecture = Lecture.get_from_ref(lecture_ref, dossier, texte)

    if lecture is not None and lecture.texte is not texte:
        # We probably created the Lecture before a new Texte was adopted
        # by the commission. Time to update with the final one!
        TexteMisAJour.create(lecture=lecture, texte=texte)
        lecture_updated = True

    if lecture is None:
        lecture = Lecture.create_from_ref(lecture_ref, dossier, texte)
        LectureCreee.create(lecture=lecture, user=user)
        lecture_created = True

    if lecture_created or lecture_updated:
        changed = True

        # Make sure the lecture gets its primary key.
        DBSession.flush()

        # Enqueue tasks to fetch articles and amendements.
        huey.enqueue_on_transaction_commit(fetch_articles.s(lecture.pk))
        huey.enqueue_on_transaction_commit(fetch_amendements.s(lecture.pk))

    return changed
