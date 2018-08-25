import transaction

from huey import crontab

from zam_repondeur import huey
from zam_repondeur.models import DBSession, Lecture
from zam_repondeur.tasks.fetch import fetch_amendements


@huey.periodic_task(crontab(minute="5", hour="*"))
def fetch_all_amendements() -> None:
    from zam_repondeur.huey_launcher import settings

    with transaction.manager:
        for lecture in DBSession.query(Lecture).all():
            fetch_amendements(lecture, settings)


# TODO: load data (get_dossiers_legislatifs and get_organes_acteurs).
# TODISCUSS: store data/references in database?
