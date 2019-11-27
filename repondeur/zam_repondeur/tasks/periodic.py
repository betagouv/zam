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


def merge_duplicate_dossiers() -> None:
    """
    Find and merge duplicate dossiers

    Some older dossiers were created from Sénat scraping that are in fact duplicates
    of ones created from AN opendata. This should not happen any more, so this
    function can be removed once all data is clean.

    Sometimes we can find the matching Sénat dossier from the AN one, and sometimes
    it's the other way, so we try both.
    """
    _merge_duplicate_dossiers_an()
    _merge_duplicate_dossiers_senat()


def _merge_duplicate_dossiers_an() -> None:
    from zam_repondeur.services.data import repository

    for dossier in DBSession.query(Dossier).filter(Dossier.senat_id.__eq__(None)):
        dossier_ref_an = repository.get_opendata_dossier_ref(dossier.an_id)
        if dossier_ref_an is None:
            continue
        dossier_ref_senat = find_matching_dossier_ref_senat(dossier_ref_an)
        if dossier_ref_senat:
            duplicate_dossier = (
                DBSession.query(Dossier)
                .filter_by(senat_id=dossier_ref_senat.uid)
                .one_or_none()
            )
            if duplicate_dossier:
                _merge_dossiers(dossier_an=dossier, dossier_senat=duplicate_dossier)


def _merge_duplicate_dossiers_senat() -> None:
    from zam_repondeur.services.data import repository

    for dossier in DBSession.query(Dossier).filter(Dossier.an_id.__eq__(None)):
        dossier_ref_senat = repository.get_senat_scraping_dossier_ref(dossier.senat_id)
        if dossier_ref_senat is None:
            continue
        dossier_ref_an = find_matching_dossier_ref_an(dossier_ref_senat)
        if dossier_ref_an:
            duplicate_dossier = (
                DBSession.query(Dossier)
                .filter_by(an_id=dossier_ref_an.uid)
                .one_or_none()
            )
            if duplicate_dossier:
                _merge_dossiers(dossier_senat=dossier, dossier_an=duplicate_dossier)


def _merge_dossiers(dossier_an: Dossier, dossier_senat: Dossier) -> None:
    # Can we delete the Sénat dossier?
    if not dossier_senat.team and not dossier_senat.lectures:
        logging.warning("Merging duplicate %r into %r", dossier_senat, dossier_an)
        senat_id = dossier_senat.senat_id
        DBSession.delete(dossier_senat)
        DBSession.flush()
        dossier_an.senat_id = senat_id
        DBSession.flush()
        return
    # Or can we delete the AN dossier?
    if not dossier_an.team and not dossier_an.lectures:
        logging.warning("Merging duplicate %r into %r", dossier_an, dossier_senat)
        an_id = dossier_an.an_id
        DBSession.delete(dossier_an)
        DBSession.flush()
        dossier_senat.an_id = an_id
        DBSession.flush()
        return
    logging.error("Cannot merge non-empty dossiers: %r, %r", dossier_an, dossier_senat)


def create_missing_dossiers_an() -> None:
    """
    Create new dossiers based on dossier_refs in AN open data
    """
    from zam_repondeur.services.data import repository

    known_an_ids = _known_an_ids()
    existing_an_ids = _existing_an_ids()
    existing_senat_ids = _existing_senat_ids()
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

    known_senat_ids = _known_senat_ids()
    existing_senat_ids = _existing_senat_ids()
    existing_an_ids = _existing_an_ids()
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


def _known_an_ids() -> Set[str]:
    from zam_repondeur.services.data import repository

    return set(repository.list_opendata_dossiers())


def _known_senat_ids() -> Set[str]:
    from zam_repondeur.services.data import repository

    return set(repository.list_senat_scraping_dossiers())


def _existing_an_ids() -> Set[str]:
    return set(
        t[0] for t in DBSession.query(Dossier.an_id).filter(Dossier.an_id.__ne__(None))
    )


def _existing_senat_ids() -> Set[str]:
    return set(
        t[0]
        for t in DBSession.query(Dossier.senat_id).filter(Dossier.senat_id.__ne__(None))
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
    for team in DBSession.query(Team).filter(Team.dossier_pk.isnot(None)):
        dossier_pk = team.dossier_pk
        delay = (dossier_pk % 15) * 60  # spread out updates over 15 minutes
        update_dossier.schedule(args=(dossier_pk,), delay=delay)
