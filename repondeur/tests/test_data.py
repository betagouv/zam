def test_list_opendata_dossiers(app):
    from zam_repondeur.data import repository

    dossiers = repository.list_opendata_dossiers()

    assert "DLR5L15N36030" in dossiers


def test_get_opendata_dossier(app):
    from zam_repondeur.data import repository
    from zam_repondeur.fetch.an.dossiers.models import DossierRef

    dossier_ref = repository.get_opendata_dossier("DLR5L15N36030")

    assert isinstance(dossier_ref, DossierRef)


def test_get_opendata_texte(app):
    from zam_repondeur.data import repository
    from zam_repondeur.fetch.an.dossiers.models import TexteRef

    texte_ref = repository.get_opendata_texte("PRJLANR5L15B0269")

    assert isinstance(texte_ref, TexteRef)


def test_get_opendata_organe(app):
    from zam_repondeur.data import repository

    organe = repository.get_opendata_organe("PO717460")

    assert isinstance(organe, dict)


def test_get_opendata_acteur(app):
    from zam_repondeur.data import repository

    acteur = repository.get_opendata_acteur("PA718838")

    assert isinstance(acteur, dict)


def test_get_senat_scraping_dossier(app):
    from zam_repondeur.data import repository
    from zam_repondeur.fetch.an.dossiers.models import DossierRef

    dossier_ref = repository.get_senat_scraping_dossier("ppl18-454")

    assert isinstance(dossier_ref, DossierRef)
