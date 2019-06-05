from zam_repondeur.data import repository
from zam_repondeur.fetch.an.dossiers.models import DossierRefsByUID


def get_dossiers_legislatifs_open_data() -> DossierRefsByUID:
    dossiers: DossierRefsByUID = repository.get_data("dossiers")
    return dossiers
