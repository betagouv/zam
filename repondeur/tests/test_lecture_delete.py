def test_lecture_delete(app, lecture_an, amendements_an):
    from zam_repondeur.models import Amendement, DBSession, Lecture

    assert Lecture.exists(
        chambre=lecture_an.chambre,
        session=lecture_an.session,
        num_texte=lecture_an.num_texte,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 2

    form = app.get("http://localhost/lectures/").forms["delete-lecture"]

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Lecture supprimée avec succès." in resp.text

    assert not Lecture.exists(
        chambre=lecture_an.chambre,
        session=lecture_an.session,
        num_texte=lecture_an.num_texte,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 0
