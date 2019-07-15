def test_dossier_delete(app, lecture_an, amendements_an, user_sgg):
    from zam_repondeur.models import Amendement, DBSession, Dossier, Lecture

    assert user_sgg.email.endswith("@sgg.pm.gouv.fr")

    assert Dossier.exists(slug="plfss-2018")
    assert Lecture.exists(
        chambre=lecture_an.chambre,
        texte=lecture_an.texte,
        partie=None,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 2

    resp = app.get("/dossiers/plfss-2018/", user=user_sgg)
    form = resp.forms["delete-dossier"]

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/dossiers/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Dossier supprimé avec succès." in resp.text

    assert Dossier.exists(slug="plfss-2018")
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
    assert "delete-dossier" not in resp.forms

    # The user bypasses the protection or we messed up.
    resp = app.post("/dossiers/plfss-2018/", user=user_david)

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/dossiers/plfss-2018/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Vous n’êtes pas autorisé à supprimer ce dossier." in resp.text

    assert Lecture.exists(
        chambre=lecture_an.chambre,
        texte=lecture_an.texte,
        partie=None,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 2
