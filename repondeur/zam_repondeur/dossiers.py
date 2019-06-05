from functools import reduce

from zam_repondeur.data import repository
from zam_repondeur.fetch.an.dossiers.models import DossierRef, DossierRefsByUID
from zam_repondeur.fetch.senat.scraping import get_dossiers_senat


def get_dossiers_legislatifs() -> DossierRefsByUID:
    dossiers = [
        get_dossiers_legislatifs_open_data(),
        get_dossiers_legislatifs_scraping_an(),
        get_dossiers_legislatifs_scraping_senat(),
    ]
    return reduce(DossierRef.merge_dossiers, dossiers, {})


def get_dossiers_legislatifs_open_data() -> DossierRefsByUID:
    dossiers: DossierRefsByUID = repository.get_data("an.opendata.dossiers")
    return dossiers


def get_dossiers_legislatifs_scraping_an() -> DossierRefsByUID:
    return {}


def get_dossiers_legislatifs_scraping_senat() -> DossierRefsByUID:
    return get_dossiers_senat()
