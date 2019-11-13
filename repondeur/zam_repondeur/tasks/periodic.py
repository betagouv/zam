"""
NB: make sure tasks.huey.init_huey() has been called before importing this module
"""
import logging
from typing import Set

from huey import crontab

from zam_repondeur.models import DBSession, Dossier, Team, Texte
from zam_repondeur.tasks.fetch import (
    find_matching_dossier_ref_an,
    find_matching_dossier_ref_senat,
    update_dossier,
)
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
    logger.info("Dossiers update start")
    create_missing_dossiers_an()
    create_missing_dossiers_senat()
    logger.info("Dossiers update end")


def create_missing_dossiers_an() -> None:
    """
    Create new dossiers based on dossier_refs in AN open data
    """
    from zam_repondeur.services.data import repository

    known_an_ids = set(repository.list_opendata_dossiers())
    existing_an_ids = set(
        t[0] for t in DBSession.query(Dossier.an_id).filter(Dossier.an_id.__ne__(None))
    )
    existing_senat_ids = set(
        t[0]
        for t in DBSession.query(Dossier.senat_id).filter(Dossier.senat_id.__ne__(None))
    )
    missing_an_ids = known_an_ids - existing_an_ids

    for an_id in missing_an_ids:

        dossier_ref_an = repository.get_opendata_dossier_ref(an_id)
        if dossier_ref_an is None:
            continue

        # Check that we have not already created from the Sénat dossier_ref
        dossier_ref_senat = find_matching_dossier_ref_senat(dossier_ref_an)
        if dossier_ref_senat:
            if dossier_ref_senat.uid in existing_senat_ids:
                continue

        senat_id = dossier_ref_senat.uid if dossier_ref_senat else None

        Dossier.create(
            an_id=an_id,
            senat_id=senat_id,
            titre=dossier_ref_an.titre,
            slug=dossier_ref_an.slug,
        )


def create_missing_dossiers_senat() -> None:
    """
    Create new dossiers based on dossier_refs scraped from Sénat web site
    """
    from zam_repondeur.services.data import repository

    known_senat_ids = set(repository.list_senat_scraping_dossiers())
    existing_senat_ids = set(
        t[0]
        for t in DBSession.query(Dossier.senat_id).filter(Dossier.senat_id.__ne__(None))
    )
    existing_an_ids = set(
        t[0] for t in DBSession.query(Dossier.an_id).filter(Dossier.an_id.__ne__(None))
    )
    missing_senat_ids = known_senat_ids - existing_senat_ids

    for senat_id in missing_senat_ids:

        dossier_ref_senat = repository.get_senat_scraping_dossier_ref(senat_id)
        if dossier_ref_senat is None:
            continue

        # Check that we have not already created from the AN dossier_ref
        dossier_ref_an = find_matching_dossier_ref_an(dossier_ref_senat)
        if dossier_ref_an:
            if dossier_ref_an.uid in existing_an_ids:
                continue

        an_id = dossier_ref_an.uid if dossier_ref_an else None

        Dossier.create(
            an_id=an_id,
            senat_id=senat_id,
            titre=dossier_ref_senat.titre,
            slug=dossier_ref_senat.slug,
        )


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
