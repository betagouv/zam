import transaction


def test_lecture_delete(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import Amendement, DBSession, Lecture

    # Make sure we have a user table for this lecture
    with transaction.manager:
        DBSession.add(user_david.table_for(lecture_an))

    assert Lecture.exists(
        chambre=lecture_an.chambre,
        session=lecture_an.session,
        num_texte=lecture_an.num_texte,
        partie=None,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 2

    resp = app.get("/lectures/an.15.269.PO717460/amendements", user="user@example.com")
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
        num_texte=lecture_an.num_texte,
        partie=None,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 0
