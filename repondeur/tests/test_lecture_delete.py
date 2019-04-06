def test_lecture_delete(app, lecture_an, amendements_an, user_david_table_an):
    from zam_repondeur.models import Amendement, DBSession, Lecture

    assert Lecture.exists(
        chambre=lecture_an.chambre,
        session=lecture_an.session,
        texte=lecture_an.texte,
        partie=None,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 2

    resp = app.get("/lectures/an.15.269.PO717460/options", user="user@zam.beta.gouv.fr")
    form = resp.forms["delete-lecture"]

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/lectures/"

    resp = resp.follow()

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/lectures/add"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Lecture supprimée avec succès." in resp.text

    assert not Lecture.exists(
        chambre=lecture_an.chambre,
        session=lecture_an.session,
        texte=lecture_an.texte,
        partie=None,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 0


def test_lecture_delete_alien_user(
    app, lecture_an, amendements_an, user_david_table_an
):
    from zam_repondeur.models import Amendement, DBSession, Lecture

    assert Lecture.exists(
        chambre=lecture_an.chambre,
        session=lecture_an.session,
        texte=lecture_an.texte,
        partie=None,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 2

    resp = app.get("/lectures/an.15.269.PO717460/options", user="user@example.com")
    assert "delete-lecture" not in resp.forms

    # The user bypasses the protection or we messed up.
    resp = app.post("/lectures/an.15.269.PO717460/", user="user@example.com")

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/lectures/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Vous n’avez pas les droits pour supprimer une lecture." in resp.text

    assert Lecture.exists(
        chambre=lecture_an.chambre,
        session=lecture_an.session,
        texte=lecture_an.texte,
        partie=None,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 2
