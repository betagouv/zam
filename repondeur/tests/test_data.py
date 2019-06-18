def test_get_dossiers(app):
    from zam_repondeur.data import repository

    dossiers = repository.get_data("an.opendata.dossiers")

    assert "DLR5L15N36030" in dossiers


def test_get_textes(app):
    from zam_repondeur.data import repository

    textes = repository.get_data("an.opendata.textes")

    assert "PRJLANR5L15B0269" in textes


def test_get_organes(app):
    from zam_repondeur.data import repository

    organes = repository.get_data("an.opendata.organes")

    assert "PO717460" in organes


def test_get_acteurs(app):
    from zam_repondeur.data import repository

    acteurs = repository.get_data("an.opendata.acteurs")

    assert "PA718838" in acteurs
