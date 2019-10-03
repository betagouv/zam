import transaction


def test_dossier_delete(app, lecture_an, amendements_an, user_sgg, team_zam):
    from zam_repondeur.models import Amendement, DBSession, Dossier, Lecture, Team

    assert Dossier.exists(slug="plfss-2018")
    assert Lecture.exists(
        dossier=lecture_an.dossier,
        texte=lecture_an.texte,
        partie=None,
        phase=lecture_an.phase,
        chambre=lecture_an.chambre,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 2
    assert DBSession.query(Team).count() == 1

    resp = app.get("/dossiers/plfss-2018/", user=user_sgg)
    form = resp.forms["delete-dossier"]

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/dossiers/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Dossier supprimé avec succès." in resp.text

    assert Dossier.exists(slug="plfss-2018")
    dossier_plfss2018 = (
        DBSession.query(Dossier).filter(Dossier.slug == lecture_an.dossier.slug).one()
    )
    assert dossier_plfss2018.team is None
    assert not Lecture.exists(
        dossier=lecture_an.dossier,
        texte=lecture_an.texte,
        partie=None,
        phase=lecture_an.phase,
        chambre=lecture_an.chambre,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 0
    assert DBSession.query(Team).count() == 0

    # We should have an event entry for the desactivation.
    assert len(dossier_plfss2018.events) == 1
    assert (
        dossier_plfss2018.events[0].render_summary()
        == "<abbr title='user@sgg.pm.gouv.fr'>SGG user</abbr> a désactivé le dossier."
    )


def test_dossier_delete_non_sgg_whitelisted_user(
    app, lecture_an, amendements_an, team_zam
):
    from zam_repondeur.models import Amendement, DBSession, Lecture, User

    with transaction.manager:
        user_sgg_not_whitelisted = User.create(
            name="SGG user 2", email="bad@sgg.pm.gouv.fr"
        )
        DBSession.add(team_zam)
        team_zam.users.append(user_sgg_not_whitelisted)

    assert Lecture.exists(
        dossier=lecture_an.dossier,
        texte=lecture_an.texte,
        partie=None,
        phase=lecture_an.phase,
        chambre=lecture_an.chambre,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 2

    resp = app.get("/dossiers/plfss-2018/", user=user_sgg_not_whitelisted)
    assert "delete-dossier" not in resp.forms

    # The user bypasses the protection or we messed up.
    resp = app.post("/dossiers/plfss-2018/", user=user_sgg_not_whitelisted)

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/dossiers/plfss-2018/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Vous n’êtes pas autorisé à supprimer ce dossier." in resp.text

    assert Lecture.exists(
        dossier=lecture_an.dossier,
        texte=lecture_an.texte,
        partie=None,
        phase=lecture_an.phase,
        chambre=lecture_an.chambre,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 2


def test_dossier_delete_non_sgg_user(
    app, lecture_an, amendements_an, user_david, user_david_table_an
):
    from zam_repondeur.models import Amendement, DBSession, Lecture

    assert not user_david.email.endswith("@sgg.pm.gouv.fr")

    assert Lecture.exists(
        dossier=lecture_an.dossier,
        texte=lecture_an.texte,
        partie=None,
        phase=lecture_an.phase,
        chambre=lecture_an.chambre,
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
        dossier=lecture_an.dossier,
        texte=lecture_an.texte,
        partie=None,
        phase=lecture_an.phase,
        chambre=lecture_an.chambre,
        organe=lecture_an.organe,
    )
    assert DBSession.query(Amendement).count() == 2
