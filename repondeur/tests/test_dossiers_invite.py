from textwrap import dedent

import transaction


def test_get_form(app, user_david, dossier_plfss2018):
    resp = app.get("/dossiers/plfss-2018/invite", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    form = resp.forms[0]
    assert form.method == "post"
    assert form.action == "https://zam.test/dossiers/plfss-2018/invite"

    assert list(form.fields.keys()) == ["emails", "save"]
    assert form.fields["save"][0].attrs["type"] == "submit"


def test_get_form_user_not_in_dossier_team(app, user_ronan, dossier_plfss2018):
    resp = app.get("/dossiers/add", user=user_ronan)

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/"

    resp = resp.maybe_follow()

    assert resp.status_code == 200
    assert "L’accès à ce dossier est réservé aux personnes autorisées." in resp.text


def test_post_form(app, user_david, dossier_plfss2018, mailer):
    from zam_repondeur.models import DBSession, Dossier

    with transaction.manager:
        DBSession.add(dossier_plfss2018)
        assert len(dossier_plfss2018.team.users) == 1
        assert dossier_plfss2018.events == []

    resp = app.get("/dossiers/plfss-2018/invite", user=user_david)
    assert resp.status_code == 200

    form = resp.forms[0]
    form["emails"] = "foo@exemple.gouv.fr"

    resp = form.submit()
    assert resp.status_code == 302

    resp = resp.follow()
    assert resp.status_code == 200

    assert "Invitation envoyée avec succès." in resp.text

    dossier_plfss2018 = (
        DBSession.query(Dossier).filter(Dossier.pk == dossier_plfss2018.pk).one()
    )
    assert len(dossier_plfss2018.team.users) == 2
    assert dossier_plfss2018.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> a invité "
        "« foo@exemple.gouv.fr »"
    )

    assert len(mailer.outbox) == 1
    assert mailer.outbox[0].recipients == ["foo@exemple.gouv.fr"]
    assert (
        mailer.outbox[0].subject
        == "Invitation à rejoindre un dossier législatif sur Zam"
    )
    assert mailer.outbox[0].body == dedent(
        """\
        Bonjour,

        Vous venez d’être invité·e à rejoindre Zam
        pour participer au dossier législatif suivant :
        Sécurité sociale : loi de financement 2018

        Veuillez vous connecter à Zam pour y accéder :
        https://zam.test/identification

        Bonne journée !"""
    )


def test_post_form_existing_user(
    app, user_david, user_ronan, dossier_plfss2018, mailer
):
    from zam_repondeur.models import DBSession, Dossier

    with transaction.manager:
        DBSession.add(user_ronan)
        DBSession.add(dossier_plfss2018)
        assert len(dossier_plfss2018.team.users) == 1
        assert dossier_plfss2018.events == []

    resp = app.get("/dossiers/plfss-2018/invite", user=user_david)
    assert resp.status_code == 200

    form = resp.forms[0]
    form["emails"] = "ronan@exemple.gouv.fr"

    resp = form.submit()
    assert resp.status_code == 302

    resp = resp.follow()
    assert resp.status_code == 200

    assert "Invitation envoyée avec succès." in resp.text

    dossier_plfss2018 = (
        DBSession.query(Dossier).filter(Dossier.pk == dossier_plfss2018.pk).one()
    )
    assert len(dossier_plfss2018.team.users) == 2
    assert dossier_plfss2018.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> a invité "
        "« ronan@exemple.gouv.fr »"
    )

    assert len(mailer.outbox) == 1
    assert mailer.outbox[0].recipients == ["ronan@exemple.gouv.fr"]
    assert (
        mailer.outbox[0].subject
        == "Invitation à participer à un dossier législatif sur Zam"
    )
    assert mailer.outbox[0].body == dedent(
        """\
        Bonjour,

        Vous venez d’être invité·e à participer
        au dossier législatif suivant sur Zam :
        Sécurité sociale : loi de financement 2018

        Vous pouvez y accéder via l’adresse suivante :
        https://zam.test/dossiers/plfss-2018/

        Bonne journée !"""
    )


def test_post_form_not_gouv(app, user_david, dossier_plfss2018):
    from zam_repondeur.models import DBSession, Dossier

    with transaction.manager:
        DBSession.add(dossier_plfss2018)
        assert len(dossier_plfss2018.team.users) == 1
        assert dossier_plfss2018.events == []

    resp = app.get("/dossiers/plfss-2018/invite", user=user_david)
    assert resp.status_code == 200

    form = resp.forms[0]
    form["emails"] = "foo@exemple.notgouv.fr"

    resp = form.submit()
    assert resp.status_code == 302

    resp = resp.follow()
    assert resp.status_code == 200

    assert (
        "Aucune invitation n’a été envoyée, veuillez vérifier "
        "les adresses de courriel qui doivent être en .gouv.fr"
    ) in resp.text

    dossier_plfss2018 = (
        DBSession.query(Dossier).filter(Dossier.pk == dossier_plfss2018.pk).one()
    )
    assert len(dossier_plfss2018.team.users) == 1
    assert dossier_plfss2018.events == []


def test_post_form_multiple_invites(app, user_david, dossier_plfss2018, mailer):
    from zam_repondeur.models import DBSession, Dossier

    with transaction.manager:
        DBSession.add(dossier_plfss2018)
        assert len(dossier_plfss2018.team.users) == 1
        assert dossier_plfss2018.events == []

    resp = app.get("/dossiers/plfss-2018/invite", user=user_david)
    assert resp.status_code == 200

    form = resp.forms[0]
    form[
        "emails"
    ] = """
        foo@exemple.gouv.fr
        bar@exemple.gouv.fr
    """

    resp = form.submit()
    assert resp.status_code == 302

    resp = resp.follow()
    assert resp.status_code == 200

    assert "Invitations envoyées avec succès." in resp.text

    dossier_plfss2018 = (
        DBSession.query(Dossier).filter(Dossier.pk == dossier_plfss2018.pk).one()
    )
    assert len(dossier_plfss2018.team.users) == 3
    assert dossier_plfss2018.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> a invité "
        "« bar@exemple.gouv.fr »"
    )
    assert dossier_plfss2018.events[1].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> a invité "
        "« foo@exemple.gouv.fr »"
    )

    assert len(mailer.outbox) == 1
    assert mailer.outbox[0].recipients == ["foo@exemple.gouv.fr", "bar@exemple.gouv.fr"]
    assert (
        mailer.outbox[0].subject
        == "Invitation à rejoindre un dossier législatif sur Zam"
    )
    assert mailer.outbox[0].body == dedent(
        """\
        Bonjour,

        Vous venez d’être invité·e à rejoindre Zam
        pour participer au dossier législatif suivant :
        Sécurité sociale : loi de financement 2018

        Veuillez vous connecter à Zam pour y accéder :
        https://zam.test/identification

        Bonne journée !"""
    )


def test_post_form_multiple_invites_one_not_gouv(app, user_david, dossier_plfss2018):
    from zam_repondeur.models import DBSession, Dossier

    with transaction.manager:
        DBSession.add(dossier_plfss2018)
        assert len(dossier_plfss2018.team.users) == 1
        assert dossier_plfss2018.events == []

    resp = app.get("/dossiers/plfss-2018/invite", user=user_david)
    assert resp.status_code == 200

    form = resp.forms[0]
    form[
        "emails"
    ] = """
        foo@exemple.gouv.fr
        bar@exemple.notgouv.fr
    """

    resp = form.submit()
    assert resp.status_code == 302

    resp = resp.follow()
    assert resp.status_code == 200

    assert "Invitation envoyée avec succès." in resp.text

    dossier_plfss2018 = (
        DBSession.query(Dossier).filter(Dossier.pk == dossier_plfss2018.pk).one()
    )
    assert len(dossier_plfss2018.team.users) == 2
    assert dossier_plfss2018.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> a invité "
        "« foo@exemple.gouv.fr »"
    )
