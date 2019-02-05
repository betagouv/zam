"""
NB: make sure tasks.huey.init_huey() has been called before importing this module
"""
import logging
from datetime import datetime

import transaction

from zam_repondeur.fetch import get_articles, get_amendements
from zam_repondeur.tasks.huey import huey
from zam_repondeur.models import DBSession, Lecture
from zam_repondeur.models.events.lecture import (
    ArticlesRecuperes,
    AmendementsNonTrouves,
    AmendementsAJour,
    AmendementsRecuperes,
    AmendementsNonRecuperes,
)


logger = logging.getLogger(__name__)


RETRY_DELAY = 5 * 60  # 5 minutes


@huey.task(retries=3, retry_delay=RETRY_DELAY)
def fetch_articles(lecture_pk: int) -> None:
    with transaction.manager, huey.lock_task(f"fetch-{lecture_pk}"):
        lecture = DBSession.query(Lecture).with_for_update().get(lecture_pk)
        if lecture is None:
            logger.error(f"Lecture {lecture_pk} introuvable")
            return

        changed: bool = get_articles(lecture)
        if changed:
            ArticlesRecuperes.create(request=None, lecture=lecture)


@huey.task(retries=3, retry_delay=RETRY_DELAY)
def fetch_amendements(lecture_pk: int) -> None:
    with transaction.manager, huey.lock_task(f"fetch-{lecture_pk}"):
        lecture = DBSession.query(Lecture).with_for_update().get(lecture_pk)
        if lecture is None:
            logger.error(f"Lecture {lecture_pk} introuvable")
            return

        amendements, created, errored = get_amendements(lecture)

        if not amendements:
            AmendementsNonTrouves.create(request=None, lecture=lecture)

        if created:
            AmendementsRecuperes.create(request=None, lecture=lecture, count=created)

        if errored:
            AmendementsNonRecuperes.create(
                request=None, lecture=lecture, missings=errored
            )

        if amendements and not (created or errored):
            AmendementsAJour.create(request=None, lecture=lecture)
        lecture.modified_at = datetime.utcnow()
