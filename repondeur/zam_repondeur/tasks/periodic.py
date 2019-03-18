"""
NB: make sure tasks.huey.init_huey() has been called before importing this module
"""
import logging

import transaction
from huey import crontab

from zam_repondeur.tasks.huey import huey
from zam_repondeur.models import DBSession, Lecture
from zam_repondeur.tasks.fetch import fetch_amendements


logger = logging.getLogger(__name__)


# TODISCUSS: hourly? daily?
@huey.periodic_task(crontab(minute="1", hour="*"))
def update_data() -> None:
    from zam_repondeur.data import repository

    logger.info("Data update start")
    repository.load_data()
    logger.info("Data update end")


# Keep it last as it takes time and will add up with the growing number of lectures.
@huey.periodic_task(crontab(minute="10", hour="*"))
def fetch_all_amendements() -> None:
    with transaction.manager:
        for lecture in DBSession.query(Lecture):
            delay = (lecture.pk % 15) * 60  # spread out updates over 15 minutes
            fetch_amendements.schedule(args=(lecture.pk,), delay=delay)
