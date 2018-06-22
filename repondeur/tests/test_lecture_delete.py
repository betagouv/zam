def test_lecture_delete(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import Amendement, DBSession, Lecture

    assert Lecture.exists(
        chambre=dummy_lecture[0], session=dummy_lecture[1], num_texte=dummy_lecture[2]
    )
    assert DBSession.query(Amendement).count() == 2

    form = app.get("http://localhost/lectures/an/15/269/").forms["delete-lecture"]

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Lecture supprimée avec succès." in resp.text

    assert not Lecture.exists(
        chambre=dummy_lecture[0], session=dummy_lecture[1], num_texte=dummy_lecture[2]
    )
    assert DBSession.query(Amendement).count() == 0
