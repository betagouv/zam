import pytest
import transaction


def test_get_list_empty(app, user_david):

    resp = app.get("/lectures/", user=user_david)

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/lectures/add"

    resp = resp.follow()

    assert resp.status_code == 200
    assert resp.content_type == "text/html"


@pytest.fixture
def lecture_commission(db, dossier_plfss2018, texte_plfss2018_an_premiere_lecture):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            texte=texte_plfss2018_an_premiere_lecture,
            titre="Numéro lecture – Titre lecture",
            organe="PO420120",
            dossier=dossier_plfss2018,
        )

    return lecture


def test_get_list_not_empty(app, lecture_an, lecture_commission, user_david):

    resp = app.get("/lectures/", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert len(resp.parser.css(".lecture")) == 3  # First one is the top link.


def test_get_list_reverse_datetime_order(app, lecture_an, user_david):
    from zam_repondeur.models import DBSession, Lecture

    with transaction.manager:
        title = str(lecture_an)
        lecture2 = Lecture.create(
            chambre=lecture_an.chambre,
            session=lecture_an.session,
            texte=lecture_an.texte,
            titre="Numéro lecture – Titre lecture 2",
            organe=lecture_an.organe,
            dossier=lecture_an.dossier,
        )
        title2 = str(lecture2)
        DBSession.add(lecture2)

    resp = app.get("/lectures/", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"
    # First one is the top link.
    assert title2 in resp.parser.css(".lecture")[1].text()
    assert title in resp.parser.css(".lecture")[2].text()


def test_team_member_can_see_owned_lecture(app, lecture_an, team_zam, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        lecture_an.owned_by_team = team_zam
        DBSession.add(user_david)
        user_david.teams.append(team_zam)
        DBSession.add(team_zam)

    resp = app.get("/lectures/", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert len(resp.parser.css(".lecture")) == 2  # First one is the top link.


def test_non_team_member_cannot_see_owned_lecture(
    app, lecture_an, team_zam, user_david
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        lecture_an.owned_by_team = team_zam
        DBSession.add(team_zam)

    resp = app.get("/lectures/", user=user_david)

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/lectures/add"
