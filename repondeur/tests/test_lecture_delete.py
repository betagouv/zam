import pytest
import transaction


@pytest.fixture
def zam_user(db, team_zam, lecture_an):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        user = User.create(name="Zam", email="user@zam.beta.gouv.fr")
        table = user.table_for(lecture_an)
        DBSession.add(table)
        return user


def test_lecture_delete(app, lecture_an, amendements_an, zam_user):
    from zam_repondeur.models import Amendement, DBSession, Lecture

    assert zam_user.email.endswith("@zam.beta.gouv.fr")

    assert Lecture.exists(
        chambre=lecture_an.chambre,
        texte=lecture_an.texte,
        partie=None,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 2

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/options", user=zam_user
    )
    form = resp.forms["delete-lecture"]

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/dossiers/plfss-2018/lectures/"

    resp = resp.follow()

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/dossiers/plfss-2018/lectures/add"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Lecture supprimée avec succès." in resp.text

    assert not Lecture.exists(
        chambre=lecture_an.chambre,
        texte=lecture_an.texte,
        partie=None,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 0


def test_lecture_delete_non_zam_user(
    app, lecture_an, amendements_an, user_david, user_david_table_an
):
    from zam_repondeur.models import Amendement, DBSession, Lecture

    assert not user_david.email.endswith("@zam.beta.gouv.fr")

    assert Lecture.exists(
        chambre=lecture_an.chambre,
        texte=lecture_an.texte,
        partie=None,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 2

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/options", user=user_david
    )
    assert "delete-lecture" not in resp.forms

    # The user bypasses the protection or we messed up.
    resp = app.post(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/", user=user_david
    )

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/dossiers/plfss-2018/lectures/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Vous n’avez pas les droits pour supprimer une lecture." in resp.text

    assert Lecture.exists(
        chambre=lecture_an.chambre,
        texte=lecture_an.texte,
        partie=None,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 2
