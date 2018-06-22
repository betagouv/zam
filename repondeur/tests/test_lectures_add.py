from datetime import date
from unittest.mock import patch

import pytest
from webtest.forms import Select


@pytest.yield_fixture(autouse=True)
def mock_dossiers_legislatifs():
    from zam_aspirateur.textes.models import Chambre, Dossier, Lecture, Texte, TypeTexte

    with patch("zam_repondeur.views.lectures.get_dossiers_legislatifs") as m_dossiers:
        m_dossiers.return_value = {
            "DLR5L15N36030": Dossier(
                uid="DLR5L15N36030",
                titre="Sécurité sociale : loi de financement 2018",
                lectures={
                    "PRJLANR5L15B0269": Lecture(
                        chambre=Chambre.AN,
                        titre="1ère lecture",
                        texte=Texte(
                            uid="PRJLANR5L15B0269",
                            type_=TypeTexte.PROJET,
                            numero=269,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 10, 11),
                        ),
                    )
                },
            )
        }
        yield


def test_get_form(app):
    resp = app.get("/lectures/add")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    assert resp.form.method == "POST"
    assert resp.form.action == "/lectures/add"

    assert list(resp.form.fields.keys()) == ["dossier", "lecture", "submit"]

    assert isinstance(resp.form.fields["dossier"][0], Select)
    assert resp.form.fields["dossier"][0].options == [
        ("DLR5L15N36030", True, "Sécurité sociale : loi de financement 2018")
    ]

    assert isinstance(resp.form.fields["lecture"][0], Select)
    assert resp.form.fields["lecture"][0].options == [
        (
            "PRJLANR5L15B0269",
            True,
            "Assemblée nationale – 1ère lecture (texte nº 269 déposé le 11/10/2017)",
        )
    ]

    assert resp.form.fields["submit"][0].attrs["type"] == "submit"


def test_post_form(app):
    from zam_repondeur.models import Lecture

    form = app.get("/lectures/add").form
    form["dossier"] = "DLR5L15N36030"
    form["lecture"] = "PRJLANR5L15B0269"

    assert not Lecture.exists(chambre="an", session="15", num_texte=269)

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an/15/269/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Lecture créée avec succès." in resp.text

    lecture = Lecture.get(chambre="an", session="15", num_texte=269)
    assert lecture.chambre == "an"
    assert lecture.titre == "1ère lecture"


def test_post_form_already_exists(app, dummy_lecture):
    from zam_repondeur.models import Lecture

    assert Lecture.exists(chambre="an", session="15", num_texte=269)

    form = app.get("/lectures/add").form
    form["dossier"] = "DLR5L15N36030"
    form["lecture"] = "PRJLANR5L15B0269"

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an/15/269/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Cette lecture existe déjà..." in resp.text
