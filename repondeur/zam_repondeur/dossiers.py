from functools import reduce

from zam_repondeur.data import repository
from zam_repondeur.fetch.an.dossiers.models import DossierRef, DossierRefsByUID


def get_dossiers_legislatifs_from_cache() -> DossierRefsByUID:
    dossiers = [
        get_dossiers_legislatifs_open_data_from_cache(),
        get_dossiers_legislatifs_scraping_an_from_cache(),
        get_dossiers_legislatifs_scraping_senat_from_cache(),
    ]
    return reduce(DossierRef.merge_dossiers, dossiers, {})


def get_dossiers_legislatifs_open_data_from_cache() -> DossierRefsByUID:
    dossiers: DossierRefsByUID = repository.get_data("an.opendata.dossiers")
    return dossiers


def get_dossiers_legislatifs_scraping_an_from_cache() -> DossierRefsByUID:
    return {}


def get_dossiers_legislatifs_scraping_senat_from_cache() -> DossierRefsByUID:
    dossiers: DossierRefsByUID = repository.get_data("senat.scraping.dossiers")
    return dossiers
