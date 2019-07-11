"""
NB: make sure tasks.huey.init_huey() has been called before importing this module
"""
import logging

from huey import crontab

from zam_repondeur.tasks.huey import huey
from zam_repondeur.models import DBSession, Dossier
from zam_repondeur.tasks.fetch import fetch_lectures


logger = logging.getLogger(__name__)


@huey.periodic_task(crontab(minute="1", hour="*"))
def update_data() -> None:
    from zam_repondeur.data import repository

    logger.info("Data update start")
    repository.load_data()
    logger.info("Data update end")


# Keep it last as it takes time and will add up with the growing number of dossiers.
@huey.periodic_task(crontab(minute="10", hour="*"))
def fetch_all_lectures() -> None:
    for dossier in DBSession.query(Dossier).filter(
        Dossier.activated_at != None
    ):  # noqa: E711
        delay = (dossier.pk % 15) * 60  # spread out updates over 15 minutes
        fetch_lectures.schedule(args=(dossier.pk,), delay=delay)
