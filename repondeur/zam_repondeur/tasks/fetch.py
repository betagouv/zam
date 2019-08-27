"""
NB: make sure tasks.huey.init_huey() has been called before importing this module
"""
import logging
from typing import Dict, Optional

from zam_repondeur.dossiers import get_dossiers_legislatifs_from_cache
from zam_repondeur.fetch import get_amendements, get_articles
from zam_repondeur.fetch.an.dossiers.models import DossierRefsByUID
from zam_repondeur.models import DBSession, Dossier, Lecture, Texte
from zam_repondeur.models.events.lecture import (
    AmendementsAJour,
    AmendementsNonRecuperes,
    AmendementsNonTrouves,
    AmendementsRecuperes,
    ArticlesRecuperes,
    LectureCreee,
)
from zam_repondeur.tasks.huey import huey

logger = logging.getLogger(__name__)


RETRY_DELAY = 5 * 60  # 5 minutes


@huey.task(retries=3, retry_delay=RETRY_DELAY)
def update_dossier(dossier_pk: int) -> None:
    with huey.lock_task(f"fetch-{dossier_pk}"):
        dossier = DBSession.query(Dossier).get(dossier_pk)
        if dossier is None:
            logger.error(f"Dossier {dossier_pk} introuvable")
            return

        get_lectures(dossier, huey.settings)


fetch_lectures = update_dossier  # backwards compatibility


def get_lectures(dossier: Dossier, settings: Dict[str, str]) -> None:

    # First fetch data from existing lectures, starting with recents.
    for lecture in reversed(dossier.lectures):
        # Refetch the lecture to apply the FOR UPDATE.
        lecture = DBSession.query(Lecture).with_for_update().get(lecture.pk)

        # Only fetch articles for recent lectures.
        if lecture.refreshable_for("articles", settings):
            fetch_articles.call_local(lecture.pk)

        # Only fetch amendements for recent lectures.
        if lecture.refreshable_for("amendements", settings):
            fetch_amendements.call_local(lecture.pk)

    # Then try to create missing lectures.
    dossiers_by_uid: DossierRefsByUID = get_dossiers_legislatifs_from_cache()
    dossier_ref = dossiers_by_uid[dossier.uid]

    for lecture_ref in reversed(dossier_ref.lectures):
        texte = Texte.get_or_create_from_ref(lecture_ref.texte, lecture_ref.chambre)
        lecture = Lecture.create_from_ref(lecture_ref, dossier, texte)
        if lecture is not None:
            LectureCreee.create(request=None, lecture=lecture)
            fetch_articles.call_local(lecture.pk)
            fetch_amendements.call_local(lecture.pk)


@huey.task(retries=3, retry_delay=RETRY_DELAY)
def fetch_articles(lecture_pk: Optional[int]) -> bool:
    if lecture_pk is None:
        return False
    with huey.lock_task(f"fetch-{lecture_pk}"):
        lecture = DBSession.query(Lecture).with_for_update().get(lecture_pk)
        if lecture is None:
            logger.error(f"Lecture {lecture_pk} introuvable")
            return False

        changed: bool = get_articles(lecture)
        if changed:
            ArticlesRecuperes.create(request=None, lecture=lecture)
        return changed


@huey.task(retries=3, retry_delay=RETRY_DELAY)
def fetch_amendements(lecture_pk: Optional[int]) -> bool:
    if lecture_pk is None:
        return False
    with huey.lock_task(f"fetch-{lecture_pk}"):
        lecture = DBSession.query(Lecture).with_for_update().get(lecture_pk)
        if lecture is None:
            logger.error(f"Lecture {lecture_pk} introuvable")
            return False

        amendements, created, errored = get_amendements(lecture)

        if not amendements:
            AmendementsNonTrouves.create(request=None, lecture=lecture)

        if created:
            AmendementsRecuperes.create(request=None, lecture=lecture, count=created)

        if errored:
            AmendementsNonRecuperes.create(
                request=None, lecture=lecture, missings=errored
            )

        changed = bool(amendements and not (created or errored))
        if changed:
            AmendementsAJour.create(request=None, lecture=lecture)
        return changed
