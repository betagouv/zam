from pathlib import Path

import responses
from webtest.forms import Select

from zam_repondeur.fetch.an.amendements import build_url


HERE = Path(__file__)
SAMPLE_DATA_DIR = HERE.parent / "fetch" / "sample_data"


def read_sample_data(basename):
    return (SAMPLE_DATA_DIR / basename).read_text()


def test_get_form(app):
    resp = app.get("/lectures/add")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    form = resp.forms["add-lecture"]
    assert form.method == "POST"
    assert form.action == "/lectures/add"

    assert list(form.fields.keys()) == ["dossier", "lecture", "submit"]

    assert isinstance(form.fields["dossier"][0], Select)
    assert form.fields["dossier"][0].options == [
        ("", True, ""),
        ("DLR5L15N36030", False, "Sécurité sociale : loi de financement 2018"),
        (
            "DLR5L15N36159",
            False,
            "Fonction publique : un Etat au service d'une société de confiance",
        ),
    ]

    assert isinstance(form.fields["lecture"][0], Select)
    assert form.fields["lecture"][0].options == [("", True, "")]

    assert form.fields["submit"][0].attrs["type"] == "submit"


@responses.activate
def test_post_form(app):
    from zam_repondeur.models import Lecture

    assert not Lecture.exists(
        chambre="an", session="15", num_texte=269, organe="PO717460"
    )

    responses.add(
        responses.GET,
        build_url(15, 269),
        body=read_sample_data("an/269/liste.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 177),
        body=read_sample_data("an/269/177.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 270),
        body=read_sample_data("an/269/270.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 723),
        body=read_sample_data("an/269/723.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 135),
        body=read_sample_data("an/269/135.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 192),
        body=read_sample_data("an/269/192.xml"),
        status=200,
    )

    responses.add(
        responses.GET,
        "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
        body=(HERE.parent / "sample_data" / "pl0269.html").read_text("utf-8", "ignore"),
        status=200,
    )

    # We cannot use form.submit() given the form is dynamic and does not
    # contain choices for lectures (dynamically loaded via JS).
    resp = app.post(
        "/lectures/add",
        {"dossier": "DLR5L15N36030", "lecture": "PRJLANR5L15B0269-PO717460"},
    )

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Lecture créée avec succès," in resp.text

    lecture = Lecture.get(chambre="an", session="15", num_texte=269, organe="PO717460")
    assert lecture.chambre == "an"
    assert lecture.titre == "Première lecture – Titre lecture"
    assert lecture.dossier_legislatif == "Sécurité sociale : loi de financement 2018"
    result = (
        "Assemblée nationale, 15e législature, Séance publique, Première lecture, "
        "texte nº\u00a0269"
    )
    assert str(lecture) == result

    # We should have a journal entry for articles, and one for amendements
    assert len(lecture.journal) == 2
    assert lecture.journal[0].kind == "info"
    assert lecture.journal[0].message == "Récupération des articles effectuée."
    assert lecture.journal[1].kind == "success"
    assert lecture.journal[1].message == f"5 nouveaux amendements récupérés."

    # We should have articles from the page (1, 2) and from the amendements (3, 8, 9)
    assert {article.num for article in lecture.articles} == {"1", "2", "3", "8", "9"}

    # We should have loaded 5 amendements
    assert [amdt.num for amdt in lecture.amendements] == [177, 270, 723, 135, 192]


def test_post_form_already_exists(app, lecture_an):
    from zam_repondeur.models import Lecture

    assert Lecture.exists(chambre="an", session="15", num_texte=269, organe="PO717460")

    # We cannot use form.submit() given the form is dynamic and does not
    # contain choices for lectures (dynamically loaded via JS).
    resp = app.post(
        "/lectures/add",
        {"dossier": "DLR5L15N36030", "lecture": "PRJLANR5L15B0269-PO717460"},
    )

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Cette lecture existe déjà..." in resp.text


def test_choices_lectures(app):

    resp = app.get("/choices/dossiers/DLR5L15N36030/")

    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/json"
    label = "Assemblée nationale – Première lecture – Titre lecture – Texte Nº 269"
    assert resp.json == {
        "lectures": [{"key": "PRJLANR5L15B0269-PO717460", "label": label}]
    }
