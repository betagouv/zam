import pytest
import transaction


@pytest.fixture
def sgg_user(db, team_zam):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        user = User.create(name="SGG user", email="user@sgg.pm.gouv.fr")
        DBSession.add(user)
        return user


def test_dossier_delete(app, lecture_an, amendements_an, sgg_user):
    from zam_repondeur.models import Amendement, DBSession, Lecture

    assert sgg_user.email.endswith("@sgg.pm.gouv.fr")

    assert Lecture.exists(
        chambre=lecture_an.chambre,
        texte=lecture_an.texte,
        partie=None,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 2

    resp = app.get("/dossiers/plfss-2018/", user=sgg_user)
    form = resp.forms["delete-lecture"]

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/dossiers/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Dossier supprimé avec succès." in resp.text

    assert not Lecture.exists(
        chambre=lecture_an.chambre,
        texte=lecture_an.texte,
        partie=None,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 0


def test_dossier_delete_non_sgg_user(
    app, lecture_an, amendements_an, user_david, user_david_table_an
):
    from zam_repondeur.models import Amendement, DBSession, Lecture

    assert not user_david.email.endswith("@sgg.pm.gouv.fr")

    assert Lecture.exists(
        chambre=lecture_an.chambre,
        texte=lecture_an.texte,
        partie=None,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 2

    resp = app.get("/dossiers/plfss-2018/", user=user_david)
    assert "delete-lecture" not in resp.forms

    # The user bypasses the protection or we messed up.
    resp = app.post("/dossiers/plfss-2018/", user=user_david)

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/dossiers/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Vous n’avez pas les droits pour supprimer un dossier." in resp.text

    assert Lecture.exists(
        chambre=lecture_an.chambre,
        texte=lecture_an.texte,
        partie=None,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 2
