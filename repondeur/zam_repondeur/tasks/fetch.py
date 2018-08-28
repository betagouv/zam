"""
NB: make sure tasks.huey.init_huey() has been called before importing this module
"""
import transaction
from datetime import datetime

from zam_repondeur.fetch import get_articles, get_amendements
from zam_repondeur.tasks.huey import huey
from zam_repondeur.models import DBSession, Journal, Lecture


@huey.task(retries=3, retry_delay=60 * 5)  # Minutes.
@huey.lock_task("fetch-articles-lock")
def fetch_articles(lecture: Lecture) -> None:
    with transaction.manager:
        get_articles(lecture)
        message = "Récupération des articles effectuée."
        Journal.create(lecture=lecture, kind="info", message=message)
        lecture.modified_at = datetime.utcnow()
        DBSession.add(lecture)


@huey.task(retries=3, retry_delay=60 * 5)  # Minutes.
@huey.lock_task("fetch-amendements-lock")
def fetch_amendements(lecture: Lecture) -> None:
    with transaction.manager:
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
        DBSession.add(lecture)
