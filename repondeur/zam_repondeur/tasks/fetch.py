"""
NB: make sure tasks.huey.init_huey() has been called before importing this module
"""
import logging
from typing import Optional

from zam_repondeur.fetch import get_amendements, get_articles
from zam_repondeur.fetch.lectures import get_lectures
from zam_repondeur.models import DBSession, Dossier, Lecture
from zam_repondeur.models.events.dossier import LecturesRecuperees
from zam_repondeur.models.events.lecture import (
    AmendementsAJour,
    AmendementsNonRecuperes,
    AmendementsNonTrouves,
    AmendementsRecuperes,
    ArticlesRecuperes,
)
from zam_repondeur.tasks.huey import huey

logger = logging.getLogger(__name__)


RETRY_DELAY = 5 * 60  # 5 minutes


@huey.task(retries=3, retry_delay=RETRY_DELAY)
def fetch_lectures(dossier_pk: int) -> None:
    with huey.lock_task(f"fetch-{dossier_pk}"):
        dossier = DBSession.query(Dossier).with_for_update().get(dossier_pk)
        if dossier is None:
            logger.error(f"Dossier {dossier_pk} introuvable")
            return

        changed: bool = get_lectures(dossier)
        if changed:
            LecturesRecuperees.create(request=None, dossier=dossier)


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
