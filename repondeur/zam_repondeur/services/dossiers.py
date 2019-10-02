from functools import reduce

from zam_repondeur.fetch.an.dossiers.models import DossierRef, DossierRefsByUID
from zam_repondeur.services.data import repository


def get_dossiers_legislatifs_from_cache() -> DossierRefsByUID:
    dossiers = [
        get_dossiers_legislatifs_open_data_from_cache(),
        get_dossiers_legislatifs_scraping_senat_from_cache(),
    ]
    return reduce(DossierRef.merge_dossiers, dossiers, {})


def get_dossiers_legislatifs_open_data_from_cache() -> DossierRefsByUID:
    dossiers: DossierRefsByUID = {
        uid: repository.get_opendata_dossier(uid)
        for uid in repository.list_opendata_dossiers()
    }
    return dossiers


def get_dossiers_legislatifs_scraping_senat_from_cache() -> DossierRefsByUID:
    dossiers: DossierRefsByUID = {
        uid: repository.get_senat_scraping_dossier(uid)
        for uid in repository.list_senat_scraping_dossiers()
    }
    return dossiers
