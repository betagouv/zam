"""
NB: make sure tasks.huey.init_huey() has been called before importing this module
"""
import logging
from datetime import datetime

import transaction

from zam_repondeur.fetch import get_articles, get_amendements
from zam_repondeur.tasks.huey import huey
from zam_repondeur.models import DBSession, Journal, Lecture


logger = logging.getLogger(__name__)


RETRY_DELAY = 5 * 60  # 5 minutes


@huey.task(retries=3, retry_delay=RETRY_DELAY)
def fetch_articles(lecture_pk: int) -> None:
    with transaction.manager, huey.lock_task(f"fetch-articles-{lecture_pk}"):

        lecture = DBSession.query(Lecture).get(lecture_pk)
        if lecture is None:
            logger.error(f"Lecture {lecture_pk} introuvable")
            return

        get_articles(lecture)

        message = "Récupération des articles effectuée."
        Journal.create(lecture=lecture, kind="info", message=message)
        lecture.modified_at = datetime.utcnow()


@huey.task(retries=3, retry_delay=RETRY_DELAY)
def fetch_amendements(lecture_pk: int) -> None:
    with transaction.manager, huey.lock_task(f"fetch-amendements-{lecture_pk}"):
        lecture = DBSession.query(Lecture).get(lecture_pk)
        if lecture is None:
            logger.error(f"Lecture {lecture_pk} introuvable")
            return

        amendements, created, errored = get_amendements(lecture)

        if not amendements:
            message = "Aucun amendement n’a pu être trouvé."
            Journal.create(lecture=lecture, kind="danger", message=message)

        if created:
            if created == 1:
                message = "1 nouvel amendement récupéré."
            else:
                message = f"{created} nouveaux amendements récupérés."
            Journal.create(lecture=lecture, kind="success", message=message)

        if errored:
            message = f"Les amendements {', '.join(errored)} n’ont pu être récupérés."
            Journal.create(lecture=lecture, kind="warning", message=message)

        if amendements and not (created or errored):
            message = "Les amendements étaient à jour."
            Journal.create(lecture=lecture, kind="info", message=message)
        lecture.modified_at = datetime.utcnow()
