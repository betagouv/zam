import re
from pathlib import Path

import responses
from webtest.forms import Select


HERE = Path(__file__)
SAMPLE_DATA_DIR = HERE.parent / "fetch" / "sample_data"


def read_sample_data(basename):
    return (SAMPLE_DATA_DIR / basename).read_text()


def test_lecture_link_in_navbar_if_at_least_one_lecture(app, lecture_an, user_david):
    resp = app.get("/lectures/add", user=user_david)
    assert 'title="Aller à la liste des lectures">Lectures</a></li>' in resp.text


def test_lecture_link_not_in_navbar_if_no_lecture(app, user_david):
    resp = app.get("/lectures/add", user=user_david)
    assert 'title="Aller à la liste des lectures">Lectures</a></li>' not in resp.text


def test_get_form(app, user_david):
    resp = app.get("/lectures/add", user=user_david)

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
        ("DLR5L15N36892", False, "Sécurité sociale : loi de financement 2019"),
    ]

    assert isinstance(form.fields["lecture"][0], Select)
    assert form.fields["lecture"][0].options == [("", True, "")]

    assert form.fields["submit"][0].attrs["type"] == "submit"


@responses.activate
def test_post_form(app, user_david):
    from zam_repondeur.models import DBSession, Lecture

    assert not DBSession.query(Lecture).all()

    responses.add(
        responses.GET,
        "http://www.assemblee-nationale.fr/eloi/15/amendements/0269/AN/liste.xml",
        body=read_sample_data("an/269/liste.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        "http://www.assemblee-nationale.fr/15/xml/amendements/0269/AN/177.xml",
        body=read_sample_data("an/269/177.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        "http://www.assemblee-nationale.fr/15/xml/amendements/0269/AN/270.xml",
        body=read_sample_data("an/269/270.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        "http://www.assemblee-nationale.fr/15/xml/amendements/0269/AN/723.xml",
        body=read_sample_data("an/269/723.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        "http://www.assemblee-nationale.fr/15/xml/amendements/0269/AN/135.xml",
        body=read_sample_data("an/269/135.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        "http://www.assemblee-nationale.fr/15/xml/amendements/0269/AN/192.xml",
        body=read_sample_data("an/269/192.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        re.compile(
            r"http://www\.assemblee-nationale\.fr/15/xml/amendements/0269/AN/\d+\.xml"
        ),
        status=404,
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
        {"dossier": "DLR5L15N36030", "lecture": "PRJLANR5L15B0269-PO717460-"},
        user=user_david,
    )

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/lectures/an.15.269.PO717460/amendements"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Lecture créée avec succès," in resp.text

    lecture = Lecture.get(
        chambre="an",
        session_or_legislature="15",
        num_texte=269,
        partie=None,
        organe="PO717460",
    )
    assert lecture.chambre == "an"
    assert lecture.titre == "Première lecture – Titre lecture"
    assert lecture.dossier.titre == "Sécurité sociale : loi de financement 2018"
    result = (
        "Assemblée nationale, 15e législature, Séance publique, Première lecture, "
        "texte nº\u00a0269"
    )
    assert str(lecture) == result

    # We should have an event entry for articles, and one for amendements
    assert len(lecture.events) == 3
    assert lecture.events[0].render_summary() == "5 nouveaux amendements récupérés."
    assert (
        lecture.events[1].render_summary() == "Le contenu des articles a été récupéré."
    )
    assert (
        lecture.events[2].render_summary()
        == "<abbr title='david@example.com'>david@example.com</abbr> a créé la lecture."
    )

    # We should have articles from the page (1, 2) and from the amendements (3, 8, 9)
    assert {article.num for article in lecture.articles} == {"1", "2", "3", "8", "9"}

    # We should have loaded 5 amendements
    assert [amdt.num for amdt in lecture.amendements] == [177, 270, 723, 135, 192]


@responses.activate
def test_post_form_senat_2019(app, user_david):
    from zam_repondeur.models import DBSession, Lecture

    assert not DBSession.query(Lecture).all()
    responses.add(
        responses.GET,
        "https://www.senat.fr/amendements/2018-2019/106/jeu_complet_2018-2019_106.csv",
        body=(
            HERE.parent
            / "fetch"
            / "sample_data"
            / "senat"
            / "jeu_complet_2018-2019_106.csv"
        ).read_bytes(),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://www.senat.fr/enseance/2018-2019/106/liste_discussion.json",
        body=(
            HERE.parent
            / "fetch"
            / "sample_data"
            / "senat"
            / "liste_discussion_106.json"
        ).read_bytes(),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://www.senat.fr/leg/pjl18-106.html",
        body=(HERE.parent / "sample_data" / "pjl18-106.html").read_text(
            "utf-8", "ignore"
        ),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv",
        body=(
            HERE.parent / "fetch" / "sample_data" / "senat" / "ODSEN_GENERAL.csv"
        ).read_bytes(),
        status=200,
    )

    # We cannot use form.submit() given the form is dynamic and does not
    # contain choices for lectures (dynamically loaded via JS).
    resp = app.post(
        "/lectures/add",
        {"dossier": "DLR5L15N36892", "lecture": "PRJLSNR5S319B0106-PO78718-"},
        user=user_david,
    )

    assert resp.status_code == 302
    assert (
        resp.location
        == "https://zam.test/lectures/senat.2018-2019.106.PO78718/amendements"
    )

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Lecture créée avec succès," in resp.text

    lecture = Lecture.get(
        chambre="senat",
        session_or_legislature="2018-2019",
        num_texte=106,
        partie=None,
        organe="PO78718",
    )
    assert lecture.chambre == "senat"
    assert lecture.titre == "Première lecture – Titre lecture"
    assert lecture.dossier.titre == "Sécurité sociale : loi de financement 2019"
    result = "Sénat, session 2018-2019, Séance publique, Première lecture, texte nº 106"
    assert str(lecture) == result

    # We should have an event entry for articles, and one for amendements
    assert len(lecture.events) == 3
    assert lecture.events[0].render_summary() == "2 nouveaux amendements récupérés."
    assert (
        lecture.events[1].render_summary() == "Le contenu des articles a été récupéré."
    )
    assert (
        lecture.events[2].render_summary()
        == "<abbr title='david@example.com'>david@example.com</abbr> a créé la lecture."
    )

    # We should have articles from the page (1) and from the amendements (19, 29)
    assert {article.num for article in lecture.articles} == {"1", "19", "29"}

    # We should have loaded 2 amendements
    assert [amdt.num for amdt in lecture.amendements] == [629, 1]


@responses.activate
def test_post_form_already_exists(
    app, texte_plfss2018_an_premiere_lecture, lecture_an, user_david
):
    from zam_repondeur.models import DBSession, Lecture

    assert Lecture.exists(
        chambre="an",
        texte=texte_plfss2018_an_premiere_lecture,
        partie=None,
        organe="PO717460",
    )

    # We cannot use form.submit() given the form is dynamic and does not
    # contain choices for lectures (dynamically loaded via JS).
    resp = app.post(
        "/lectures/add",
        {"dossier": "DLR5L15N36030", "lecture": "PRJLANR5L15B0269-PO717460-"},
        user=user_david,
    )

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/lectures/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Cette lecture existe déjà…" in resp.text

    DBSession.add(lecture_an)
    assert len(lecture_an.events) == 0


def test_choices_lectures(app, user_david):

    resp = app.get("/choices/dossiers/DLR5L15N36030/", user=user_david)

    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/json"
    label_an = "Assemblée nationale – Première lecture – Titre lecture – Texte Nº 269"
    label_senat = "Sénat – Première lecture – Titre lecture – Texte Nº 63"
    assert resp.json == {
        "lectures": [
            {"key": "PRJLANR5L15B0269-PO717460-", "label": label_an},
            {"key": "PRJLSNR5S299B0063-PO78718-", "label": label_senat},
        ]
    }
