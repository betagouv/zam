from textwrap import dedent

import pytest
import transaction


@pytest.fixture(autouse=True)
def extra_whitelist(db):
    from zam_repondeur.models.users import AllowedEmailPattern

    with transaction.manager:
        AllowedEmailPattern.create(pattern="liste.blanche@exemple.fr")


def test_menu_action(app, user_david, dossier_plfss2018):
    resp = app.get("/dossiers/plfss-2018/", user=user_david)
    menu_actions = [
        elem.text().strip() for elem in resp.parser.css(".menu-actions > li > a")
    ]
    assert "Inviter au dossier" in menu_actions


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
        par David (david@exemple.gouv.fr)
        pour participer au dossier législatif suivant :
        Sécurité sociale : loi de financement 2018

        Vous pouvez y accéder via l’adresse suivante :
        https://zam.test/dossiers/plfss-2018/

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

        Vous venez d’être invité·e
        par David (david@exemple.gouv.fr) à participer
        au dossier législatif suivant sur Zam :
        Sécurité sociale : loi de financement 2018

        Vous pouvez y accéder via l’adresse suivante :
        https://zam.test/dossiers/plfss-2018/

        Bonne journée !"""
    )


@pytest.mark.parametrize(
    "email", ["foo@exemple.notgouv.fr", "nótasçii@exemple.gouv.fr"]
)
def test_post_form_invalid_address(app, user_david, dossier_plfss2018, email):
    from zam_repondeur.models import DBSession, Dossier

    with transaction.manager:
        DBSession.add(dossier_plfss2018)
        assert len(dossier_plfss2018.team.users) == 1
        assert dossier_plfss2018.events == []

    resp = app.get("/dossiers/plfss-2018/invite", user=user_david)
    assert resp.status_code == 200

    form = resp.forms[0]
    form["emails"] = email

    resp = form.submit()
    assert resp.status_code == 302

    resp = resp.follow()
    assert resp.status_code == 200

    assert "Aucune invitation n’a été envoyée." in resp.text

    assert (
        f"L’adresse courriel {email} "
        "est mal formée ou non autorisée et n’a pas été invitée."
    ) in resp.text

    dossier_plfss2018 = (
        DBSession.query(Dossier).filter(Dossier.pk == dossier_plfss2018.pk).one()
    )
    assert len(dossier_plfss2018.team.users) == 1
    assert dossier_plfss2018.events == []


def test_post_form_xss_address(app, user_david, dossier_plfss2018):
    from zam_repondeur.models import DBSession, Dossier

    with transaction.manager:
        DBSession.add(dossier_plfss2018)
        assert len(dossier_plfss2018.team.users) == 1
        assert dossier_plfss2018.events == []

    resp = app.get("/dossiers/plfss-2018/invite", user=user_david)
    assert resp.status_code == 200

    form = resp.forms[0]
    form["emails"] = "<script>alert('xss')</script>"

    resp = form.submit()
    assert resp.status_code == 302

    resp = resp.follow()
    assert resp.status_code == 200

    assert "Aucune invitation n’a été envoyée." in resp.text

    assert (
        "L’adresse courriel &lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt; "
        "est mal formée ou non autorisée et n’a pas été invitée."
    ) in resp.text

    dossier_plfss2018 = (
        DBSession.query(Dossier).filter(Dossier.pk == dossier_plfss2018.pk).one()
    )
    assert len(dossier_plfss2018.team.users) == 1
    assert dossier_plfss2018.events == []


def test_post_form_already_invited(app, user_david, dossier_plfss2018):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(dossier_plfss2018)
        assert len(dossier_plfss2018.team.users) == 1
        assert dossier_plfss2018.events == []

    for _ in range(2):
        resp = app.get("/dossiers/plfss-2018/invite", user=user_david)
        assert resp.status_code == 200

        form = resp.forms[0]
        form["emails"] = "foo@exemple.gouv.fr"

        resp = form.submit().maybe_follow()
        assert resp.status_code == 200

    assert "Aucune invitation n’a été envoyée." in resp.text

    assert (
        "L’adresse courriel foo@exemple.gouv.fr "
        "avait déjà été invitée au dossier précédemment."
    ) in resp.text


def test_post_form_whitelisted(app, user_david, dossier_plfss2018):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(dossier_plfss2018)
        assert len(dossier_plfss2018.team.users) == 1
        assert dossier_plfss2018.events == []

    resp = app.get("/dossiers/plfss-2018/invite", user=user_david)
    assert resp.status_code == 200

    form = resp.forms[0]
    form["emails"] = "liste.blanche@exemple.fr"

    resp = form.submit()
    assert resp.status_code == 302

    resp = resp.follow()
    assert resp.status_code == 200

    assert "Invitation envoyée avec succès." in resp.text


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

    assert len(mailer.outbox) == 2
    assert mailer.outbox[0].sender == "contact@zam.beta.gouv.fr"
    assert mailer.outbox[0].extra_headers["reply-to"] == "David <david@exemple.gouv.fr>"
    assert mailer.outbox[0].recipients == ["foo@exemple.gouv.fr"]
    assert (
        mailer.outbox[0].subject
        == "Invitation à rejoindre un dossier législatif sur Zam"
    )
    assert mailer.outbox[0].body == dedent(
        """\
        Bonjour,

        Vous venez d’être invité·e à rejoindre Zam
        par David (david@exemple.gouv.fr)
        pour participer au dossier législatif suivant :
        Sécurité sociale : loi de financement 2018

        Vous pouvez y accéder via l’adresse suivante :
        https://zam.test/dossiers/plfss-2018/

        Bonne journée !"""
    )
    assert mailer.outbox[1].recipients == ["bar@exemple.gouv.fr"]
    assert mailer.outbox[1].sender == "contact@zam.beta.gouv.fr"
    assert mailer.outbox[1].extra_headers["reply-to"] == "David <david@exemple.gouv.fr>"
    assert (
        mailer.outbox[1].subject
        == "Invitation à rejoindre un dossier législatif sur Zam"
    )
    assert mailer.outbox[1].body == dedent(
        """\
        Bonjour,

        Vous venez d’être invité·e à rejoindre Zam
        par David (david@exemple.gouv.fr)
        pour participer au dossier législatif suivant :
        Sécurité sociale : loi de financement 2018

        Vous pouvez y accéder via l’adresse suivante :
        https://zam.test/dossiers/plfss-2018/

        Bonne journée !"""
    )


def test_post_form_multiple_invites_one_not_gouv(
    app, user_david, dossier_plfss2018, mailer
):
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

    assert (
        "L’adresse courriel bar@exemple.notgouv.fr "
        "est mal formée ou non autorisée et n’a pas été invitée."
    ) in resp.text

    dossier_plfss2018 = (
        DBSession.query(Dossier).filter(Dossier.pk == dossier_plfss2018.pk).one()
    )
    assert len(dossier_plfss2018.team.users) == 2
    assert dossier_plfss2018.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> a invité "
        "« foo@exemple.gouv.fr »"
    )

    assert len(mailer.outbox) == 1
