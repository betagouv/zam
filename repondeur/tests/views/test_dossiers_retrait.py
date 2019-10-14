import transaction


def test_get_form(app, user_sgg, user_david, dossier_plfss2018):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(dossier_plfss2018)
        dossier_plfss2018.team.users.append(user_david)

    resp = app.get("/dossiers/plfss-2018/retrait", user=user_sgg)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    assert len(resp.forms) == 1
    form = resp.forms[0]
    assert form.method == "post"
    assert form.action == "https://zam.test/dossiers/plfss-2018/retrait"

    assert list(form.fields.keys()) == ["pk", "save"]
    assert form.fields["pk"][0].value == str(user_david.pk)
    assert form.fields["save"][0].attrs["type"] == "submit"


def test_get_form_not_kicking_itself(app, user_sgg, user_david, dossier_plfss2018):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(dossier_plfss2018)
        dossier_plfss2018.team.users.append(user_sgg)
        dossier_plfss2018.team.users.append(user_david)

    resp = app.get("/dossiers/plfss-2018/retrait", user=user_sgg)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert len(resp.forms) == 1


def test_get_form_not_admin(app, user_sgg, user_david, dossier_plfss2018):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(dossier_plfss2018)
        dossier_plfss2018.team.users.append(user_david)

    resp = app.get("/dossiers/plfss-2018/retrait", user=user_david)

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/dossiers/plfss-2018/"

    resp = resp.maybe_follow()

    assert resp.status_code == 200
    assert "Vous n’êtes pas autorisé à retirer une personne de ce dossier." in resp.text


def test_post_form(app, user_sgg, user_david, dossier_plfss2018, mailer):
    from zam_repondeur.models import DBSession, Dossier

    with transaction.manager:
        DBSession.add(dossier_plfss2018)
        dossier_plfss2018.team.users.append(user_david)
        assert dossier_plfss2018.events == []

    resp = app.get("/dossiers/plfss-2018/retrait", user=user_sgg)
    assert resp.status_code == 200

    form = resp.forms[0]
    resp = form.submit()
    assert resp.status_code == 302
    assert resp.location == "https://zam.test/dossiers/plfss-2018/retrait"

    resp = resp.follow()
    assert resp.status_code == 200

    assert (
        "David (david@exemple.gouv.fr) a été retiré·e du dossier avec succès."
        in resp.text
    )

    dossier_plfss2018 = (
        DBSession.query(Dossier).filter(Dossier.pk == dossier_plfss2018.pk).one()
    )
    assert len(dossier_plfss2018.team.users) == 0
    assert dossier_plfss2018.events[0].render_summary() == (
        "<abbr title='user@sgg.pm.gouv.fr'>SGG user</abbr> a retiré "
        "« David (david@exemple.gouv.fr) »"
    )
