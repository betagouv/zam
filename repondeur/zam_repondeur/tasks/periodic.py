"""
NB: make sure tasks.huey.init_huey() has been called before importing this module
"""
import logging

from huey import crontab

from zam_repondeur.dossiers import get_dossiers_legislatifs_from_cache
from zam_repondeur.fetch.an.dossiers.models import DossierRefsByUID
from zam_repondeur.models import DBSession, Dossier, Team, Texte
from zam_repondeur.tasks.fetch import update_dossier
from zam_repondeur.tasks.huey import huey

logger = logging.getLogger(__name__)


@huey.periodic_task(crontab(minute="1", hour="*"))
def update_data() -> None:
    update_data_repository()
    update_textes_and_dossiers()


def update_data_repository() -> None:
    """
    Fetch AN open data, scrape Sénat dossiers, and put everything in Redis cache
    """
    from zam_repondeur.data import repository

    logger.info("Data update start")
    repository.load_data()
    logger.info("Data update end")


def update_textes_and_dossiers() -> None:
    """
    Update Textes and Dossiers in database based on data in Redis cache
    """
    logger.info("Textes and dossiers update start")
    dossiers_by_uid = get_dossiers_legislatifs_from_cache()
    create_missing_dossiers(dossiers_by_uid)
    create_missing_textes(dossiers_by_uid)
    logger.info("Textes and dossiers update end")


def create_missing_dossiers(dossiers_by_uid: DossierRefsByUID) -> None:
    existing_dossiers = set(t[0] for t in DBSession.query(Dossier.uid))
    for uid, dossier_ref in dossiers_by_uid.items():
        if uid not in existing_dossiers:
            Dossier.create(uid=uid, titre=dossier_ref.titre, slug=dossier_ref.slug)


def create_missing_textes(dossiers_by_uid: DossierRefsByUID) -> None:
    existing_textes = set(
        DBSession.query(Texte.chambre, Texte.session, Texte.legislature, Texte.numero)
    )
    texte_refs = {
        lecture_ref.texte
        for dossier_ref in dossiers_by_uid.values()
        for lecture_ref in dossier_ref.lectures
    }
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
