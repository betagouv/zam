import pytest
import transaction


def test_get_list_empty(app):

    resp = app.get("/lectures/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert "Aucune lecture pour l’instant." in resp.text


@pytest.fixture
def lecture_commission(app):
    from zam_repondeur.models import DBSession, Lecture

    with transaction.manager:
        lecture = Lecture(
            chambre="an",
            session="15",
            num_texte=269,
            titre="Titre lecture",
            organe="PO420120",
        )
        DBSession.add(lecture)

    return lecture


def test_get_list_not_empty(app, lecture_an, lecture_commission):

    resp = app.get("/lectures/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    links = resp.parser.css("td a")
    assert [link.text() for link in links] == [
        "Assemblée nationale, 15e législature, Séance publique, texte nº 269",
        "Assemblée nationale, 15e législature, Commission des affaires sociales, texte nº 269",  # noqa
    ]
    assert links[0].attributes["href"] != links[1].attributes["href"]


def test_get_list_reverse_datetime_order(app, lecture_an):
    from zam_repondeur.models import DBSession, Lecture

    with transaction.manager:
        title = str(lecture_an)
        lecture2 = Lecture.create(
            chambre=lecture_an.chambre,
            session=lecture_an.session,
            num_texte=lecture_an.num_texte + 1,
            titre="Titre lecture 2",
            organe=lecture_an.organe,
            dossier_legislatif=lecture_an.dossier_legislatif,
        )
        title2 = str(lecture2)
        DBSession.add(lecture2)

    resp = app.get("/lectures/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"
    assert title in resp.text
    assert title2 in resp.text
    assert resp.parser.css("tbody a")[0].text() == title2
    assert resp.parser.css("tbody a")[1].text() == title
