import pytest
import transaction


def test_get_list_empty(app):

    resp = app.get("/lectures/")

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/add"

    resp = resp.follow()

    assert resp.status_code == 200
    assert resp.content_type == "text/html"


@pytest.fixture
def lecture_commission(app):
    from zam_repondeur.models import DBSession, Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            num_texte=269,
            titre="Titre lecture",
            organe="PO420120",
            dossier_legislatif="Titre dossier legislatif",
        )
        DBSession.add(lecture)

    return lecture


@pytest.mark.xfail
def test_get_list_not_empty(app, lecture_an, lecture_commission):

    resp = app.get("/lectures/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert len(resp.parser.css(".card")) == 2


@pytest.mark.xfail
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
    assert title2 in resp.parser.css(".card")[0].text()
    assert title in resp.parser.css(".card")[1].text()
