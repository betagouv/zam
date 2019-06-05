from zam_repondeur.data import repository
from zam_repondeur.fetch.an.dossiers.models import DossierRefsByUID
from zam_repondeur.fetch.senat.scraping import get_dossiers_senat


def get_dossiers_legislatifs_open_data() -> DossierRefsByUID:
    dossiers: DossierRefsByUID = repository.get_data("dossiers")
    return dossiers


def get_dossiers_legislatifs_scraping_an() -> DossierRefsByUID:
    return {}


def get_dossiers_legislatifs_scraping_senat() -> DossierRefsByUID:
    return get_dossiers_senat()
