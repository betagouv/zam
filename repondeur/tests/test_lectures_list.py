import pytest
import transaction


def test_get_list_empty(app):

    resp = app.get("/lectures/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert "Aucune lecture pour l’instant." in resp.text


@pytest.fixture
def dummy_lecture_commission(app):
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


def test_get_list_not_empty(app, dummy_lecture, dummy_lecture_commission):

    resp = app.get("/lectures/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    links = resp.parser.css("td a")
    assert [link.text() for link in links] == [
        "Assemblée nationale, 15e législature, Commission des affaires sociales, texte nº 269",  # noqa
        "Assemblée nationale, 15e législature, Séance publique, texte nº 269",
    ]
    assert links[0].attributes["href"] != links[1].attributes["href"]
