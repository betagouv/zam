import pytest
import transaction


def test_get_list_empty(app, dossier_plfss2018, user_david):

    resp = app.get("/dossiers/plfss-2018/lectures/", user=user_david)

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/dossiers/plfss-2018/lectures/add"

    resp = resp.follow()

    assert resp.status_code == 200
    assert resp.content_type == "text/html"


@pytest.fixture
def lecture_commission(db, dossier_plfss2018, texte_plfss2018_an_premiere_lecture):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            texte=texte_plfss2018_an_premiere_lecture,
            titre="Numéro lecture – Titre lecture",
            organe="PO420120",
            dossier=dossier_plfss2018,
        )

    return lecture


def test_get_list_not_empty(app, lecture_an, lecture_commission, user_david):

    resp = app.get("/dossiers/plfss-2018/lectures/", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert len(resp.parser.css(".lecture")) == 3  # First one is the top link.


def test_get_list_reverse_datetime_order(app, lecture_an, user_david):
    from zam_repondeur.models import DBSession, Lecture

    with transaction.manager:
        title = str(lecture_an)
        lecture2 = Lecture.create(
            texte=lecture_an.texte,
            titre="Numéro lecture – Titre lecture 2",
            organe=lecture_an.organe,
            dossier=lecture_an.dossier,
        )
        title2 = str(lecture2)
        DBSession.add(lecture2)

    resp = app.get("/dossiers/plfss-2018/lectures/", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"
    # First one is the top link.
    assert title2 in resp.parser.css(".lecture")[1].text()
    assert title in resp.parser.css(".lecture")[2].text()
