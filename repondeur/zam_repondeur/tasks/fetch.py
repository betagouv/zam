"""
NB: make sure tasks.huey.init_huey() has been called before importing this module
"""
import logging
from typing import Optional

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
from zam_repondeur.services.fetch.amendements import RemoteSource
from zam_repondeur.services.fetch.an.dossiers.models import DossierRef, LectureRef
from zam_repondeur.services.fetch.senat.scraping import scrape_dossier
from zam_repondeur.tasks.huey import huey

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

        # This allows disabling the prefetching in tests.
        prefetching_enabled = int(huey.settings["zam.http_cache_duration"]) > 0

        source = RemoteSource.get_remote_source_for_chambre(
            chambre=lecture.chambre, prefetching_enabled=prefetching_enabled
        )

        # Prefetch URLs into the requests cached session.
        source.prepare(lecture)

        # Then perform the actual update,the idea is to minimize the duration
        # of the locks on the lecture and on the updated amendements.
        lecture = DBSession.query(Lecture).with_for_update().get(lecture_pk)
        if lecture is None:
            logger.error(f"Lecture {lecture_pk} introuvable")
            return False

        amendements, created, errored = source.fetch(lecture)

        if not amendements:
            AmendementsNonTrouves.create(lecture=lecture)

        if created:
            AmendementsRecuperes.create(lecture=lecture, count=created)

        if errored:
            AmendementsNonRecuperes.create(lecture=lecture, missings=errored)

        changed = bool(amendements and not (created or errored))
        if changed:
            AmendementsAJour.create(lecture=lecture)

        return changed


@huey.task()
def create_missing_lectures(dossier_pk: int, user_pk: Optional[int] = None) -> None:
    with huey.lock_task(f"dossier-{dossier_pk}"):
        dossier = DBSession.query(Dossier).get(dossier_pk)
        if dossier is None:
            logger.error(f"Dossier {dossier_pk} introuvable")
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
    dossier_ref_open_data = repository.get_dossier_ref(dossier.uid)
    # FIXME: error handling

    changed = False
    for lecture_ref in dossier_ref_open_data.lectures:
        if lecture_ref.chambre == Chambre.AN:
            changed |= do_something(dossier, lecture_ref, user)
    return changed


def create_missing_lectures_senat(dossier: Dossier, user: Optional[User]) -> bool:
    # Start with the information in AN Open Data, which may be incomplete
    dossier_ref_open_data = repository.get_dossier_ref(dossier.uid)

    dossier_id = dossier_ref_open_data.senat_dossier_id
    if dossier_id is None:
        return False

    assert dossier_ref_open_data.senat_url is not None  # mypy hint

    # From there, get fresh data from the Sénat web site
    dossier_ref_senat = get_senat_dossier_ref_from_cache_or_scrape(
        dossier_id=dossier_id, webpage_url=dossier_ref_open_data.senat_url
    )

    changed = False
    for lecture_ref in dossier_ref_senat.lectures:
        if lecture_ref.chambre == Chambre.SENAT:
            logger.info(lecture_ref)
            changed |= do_something(dossier, lecture_ref, user)
    return changed


def get_senat_dossier_ref_from_cache_or_scrape(
    dossier_id: str, webpage_url: str
) -> DossierRef:
    """
    Get dossier from the Redis cache (if recent) or scrape it
    """
    dossier_ref_senat = repository.get_senat_scraping_dossier(dossier_id)
    if dossier_ref_senat is None:
        dossier_ref_senat = scrape_dossier(dossier_id)
    return dossier_ref_senat


def do_something(
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


# dossiers_by_uid: DossierRefsByUID = get_dossiers_legislatifs_from_cache()
# try:
#     dossier_ref = dossiers_by_uid[dossier.uid]
# except KeyError:
#     logger.warning(f"Missing key for dossier {dossier.uid}")
#     return

# changed = False

# lecture_refs = list(reversed(dossier_ref.lectures))
# from pprint import pformat

# logger.info(pformat(lecture_refs))
# for lecture_ref in lecture_refs:
