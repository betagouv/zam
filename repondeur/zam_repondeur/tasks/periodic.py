"""
NB: make sure tasks.huey.init_huey() has been called before importing this module
"""
import logging
from typing import Set

from huey import crontab

from zam_repondeur.models import DBSession, Dossier, Team, Texte
from zam_repondeur.tasks.fetch import update_dossier
from zam_repondeur.tasks.huey import huey

logger = logging.getLogger(__name__)


@huey.periodic_task(crontab(minute="1", hour="*"))
def update_data() -> None:
    update_data_repository()
    update_dossiers()
    update_textes()


def update_data_repository() -> None:
    """
    Fetch AN open data, scrape Sénat dossiers, and put everything in Redis cache
    """
    from zam_repondeur.services.data import repository

    logger.info("Data update start")
    repository.load_data()
    logger.info("Data update end")


def update_dossiers() -> None:
    """
    Update Dossiers in database based on data in Redis cache
    """
    from zam_repondeur.services.data import repository

    logger.info("Dossiers update start")
    dossiers_opendata = set(repository.list_opendata_dossiers())
    dossiers_scraping = set(repository.list_senat_scraping_dossiers())
    create_missing_dossiers(dossiers_opendata | dossiers_scraping)
    logger.info("Dossiers update end")


def create_missing_dossiers(all_dossiers: Set[str]) -> None:
    from zam_repondeur.services.data import repository

    existing_dossiers = set(t[0] for t in DBSession.query(Dossier.uid))
    missing_dossiers = all_dossiers - existing_dossiers
    for uid in missing_dossiers:
        dossier_ref = repository.get_dossier_ref(uid)
        Dossier.create(uid=uid, titre=dossier_ref.titre, slug=dossier_ref.slug)


def update_textes() -> None:
    """
    Update Textes in database based on data in Redis cache
    """
    from zam_repondeur.services.data import repository

    logger.info("Textes update start")
    create_missing_textes(set(repository.list_opendata_textes()))
    logger.info("Textes  update end")


def create_missing_textes(all_textes: Set[str]) -> None:
    from zam_repondeur.services.data import repository

    existing_textes = set(
        DBSession.query(Texte.chambre, Texte.session, Texte.legislature, Texte.numero)
    )
    texte_refs = {repository.get_opendata_texte(uid) for uid in all_textes}
    new_texte_refs = {
        texte_ref
        for texte_ref in texte_refs
        if (
            texte_ref.chambre,
            texte_ref.session,
            texte_ref.legislature,
            texte_ref.numero,
        )
        not in existing_textes
    }
    for texte_ref in new_texte_refs:
        if texte_ref.date_depot is None:
            logger.warning("missing date_depot in TexteRef(uid=%r)", texte_ref.uid)
            continue
        Texte.create(
            type_=texte_ref.type_,
            chambre=texte_ref.chambre,
            session=texte_ref.session,
            legislature=texte_ref.legislature,
            numero=texte_ref.numero,
            date_depot=texte_ref.date_depot,
        )


# Keep it last as it takes time and will add up with the growing number of dossiers.
@huey.periodic_task(crontab(minute="10", hour="*"))
def update_all_dossiers() -> None:
    for team in DBSession.query(Team):
        dossier_pk = team.dossier.pk
        delay = (dossier_pk % 15) * 60  # spread out updates over 15 minutes
        update_dossier.schedule(args=(dossier_pk,), delay=delay)
