from zam_repondeur.services.data import repository
from zam_repondeur.services.fetch.an.dossiers.models import DossierRefsByUID


def get_dossiers_legislatifs_open_data_from_cache() -> DossierRefsByUID:
    dossiers: DossierRefsByUID = {
        uid: repository.get_opendata_dossier_ref(uid)
        for uid in repository.list_opendata_dossiers()
    }
    return dossiers


def get_dossiers_legislatifs_scraping_senat_from_cache() -> DossierRefsByUID:
    dossiers: DossierRefsByUID = {
        uid: repository.get_senat_scraping_dossier_ref(uid)
        for uid in repository.list_senat_scraping_dossiers()
    }
    return dossiers
