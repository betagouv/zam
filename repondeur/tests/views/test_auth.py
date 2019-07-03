import logging
import time
from datetime import datetime, timedelta, timezone
from textwrap import dedent
from unittest.mock import patch

import pytest
import transaction
from freezegun import freeze_time


@pytest.fixture
def email():
    return "david@exemple.gouv.fr"


@pytest.fixture
def auth_token(email):
    from zam_repondeur.users import repository

    token = "FOOBARBA"
    repository.set_auth_token(email, token)
    yield token
    repository.delete_auth_token(token)


class TestLoginPage:
    def test_unauthentified_user_can_view_login_page(self, app):
        resp = app.get("/identification")
        assert resp.status_code == 200

    @pytest.mark.parametrize(
        "valid_email", ["foo@exemple.gouv.fr", "BAR@EXEMPLE.GOUV.FR"]
    )
    def test_an_email_with_a_token_is_sent_if_address_is_valid(
        self, app, mailer, valid_email
    ):

        with patch(
            "zam_repondeur.views.auth.generate_auth_token"
        ) as mock_generate_auth_token:
            mock_generate_auth_token.return_value = "FOOBARBA"

            resp = app.post("/identification", {"email": valid_email})

        resp = resp.maybe_follow()

        assert "Vous devriez recevoir un lien dans les minutes" in resp.text

        assert len(mailer.outbox) == 1
        assert mailer.outbox[0].subject == "Se connecter à Zam"
        assert mailer.outbox[0].body == dedent(
            """\
            Bonjour,

            Pour vous connecter à Zam, veuillez cliquer sur l’adresse suivante :
            https://zam.test/authentification?token=FOOBARBA

            Bonne journée !"""
        )

    def test_user_cannot_ask_for_a_token_with_a_missing_email(self, app):
        resp = app.post("/identification", {"email": ""})

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/identification"
        resp = resp.follow()
        assert "La saisie d’une adresse de courriel est requise." in resp.text

    @pytest.mark.parametrize("incorrect_email", [" ", "foo"])
    def test_user_cannot_ask_for_a_token_with_an_invalid_email(
        self, app, incorrect_email
    ):
        resp = app.post("/identification", {"email": incorrect_email})

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/identification"
        resp = resp.follow()
        assert "La saisie d’une adresse de courriel valide est requise." in resp.text

    @pytest.mark.parametrize(
        "notgouvfr_email",
        [
            "jane.doe@example.com",
            "john@notgouv.fr",
            "fs0c131y@exemple.gouv.fr@example.com",
        ],
    )
    def test_user_cannot_ask_for_a_token_with_an_invalid_domain_name(
        self, app, notgouvfr_email
    ):
        resp = app.post("/identification", {"email": notgouvfr_email})

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/identification"
        resp = resp.follow()
        assert "Cette adresse de courriel n’est pas en .gouv.fr." in resp.text


class TestLoginWithToken:
    def test_user_can_login_with_auth_token(self, app, auth_token):

        resp = app.get("/authentification", params={"token": auth_token})

        assert resp.status_code == 302
        assert (
            resp.location
            == "https://zam.test/bienvenue?source=https%3A%2F%2Fzam.test%2Flectures%2F"
        )

        resp = resp.maybe_follow()

        assert "Bienvenue dans Zam" in resp.text

    def test_successful_authentication_attempt_is_logged(self, app, auth_token, caplog):
        caplog.set_level(logging.INFO)
        app.get("/authentification", params={"token": auth_token})
        assert (
            "INFO Successful authentication by 'david@exemple.gouv.fr' from 127.0.0.1"  # noqa
            in caplog.text
        )

    def test_user_cannot_login_with_bad_auth_token(self, app, auth_token):

        resp = app.get("/authentification", params={"token": "BADTOKEN"})

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/identification"

        resp = resp.maybe_follow()

        assert "Le lien est invalide ou a expiré" in resp.text

    def test_failed_authentication_attempt_is_logged(self, app, auth_token, caplog):
        app.get("/authentification", params={"token": "BADTOKEN"})
        assert (
            "WARNING Failed authentication attempt with token 'BADTOKEN' from 127.0.0.1"  # noqa
            in caplog.text
        )

    def test_authenticated_user_gets_an_auth_cookie(self, app, auth_token):
        assert "auth_tkt" not in app.cookies  # no auth cookie yet

        app.get("/authentification", params={"token": auth_token})

        assert "auth_tkt" in app.cookies  # and now we have the auth cookie

        domains = {cookie.domain for cookie in app.cookiejar}
        assert domains == {".zam.test", "zam.test"}

        auth_cookies = [cookie for cookie in app.cookiejar if cookie.name == "auth_tkt"]
        for cookie in auth_cookies:
            assert cookie.path == "/"
            assert cookie.secure is True

            # Auth cookie should expire after 7 days
            assert cookie.expires == int(time.time()) + (7 * 24 * 3600)

            # We want users to be able to follow an e-mailed link to the app
            # (see: https://www.owasp.org/index.php/SameSite)
            assert cookie.get_nonstandard_attr("SameSite") == "Lax"

    def test_auth_token_is_deleted_after_use(self, app, auth_token):
        from zam_repondeur.users import repository

        assert repository.get_auth_token_data(auth_token) is not None  # token is here

        app.get("/authentification", params={"token": auth_token})

        assert repository.get_auth_token_data(auth_token) is None  # token is gone


class TestLogout:
    def test_user_loses_the_auth_cookie_when_logging_out(self, app, auth_token):

        app.get("/authentification", params={"token": auth_token})
        assert "auth_tkt" in app.cookies  # the auth cookie is set

        app.get("/deconnexion")
        assert "auth_tkt" not in app.cookies  # the auth cookie is gone


class TestAuthenticationRequired:
    def test_unauthenticated_user_is_redirected_to_login_page(self, app):
        resp = app.get("/lectures/add")
        assert resp.status_code == 302
        assert resp.location == (
            "https://zam.test/identification"
            "?source=https%3A%2F%2Fzam.test%2Flectures%2Fadd"
        )

    def test_authenticated_user_is_not_redirected_to_login_page(self, app, user_david):
        resp = app.get("/lectures/add", user=user_david)
        assert resp.status_code == 200


class TestOnboarding:
    def test_new_user_must_enter_their_name_on_the_welcome_page(self, app):
        from zam_repondeur.auth import generate_auth_token
        from zam_repondeur.models import DBSession, User
        from zam_repondeur.users import repository

        user = DBSession.query(User).filter_by(email="jane.doe@exemple.gouv.fr").first()
        assert user is None

        token = generate_auth_token()

        repository.set_auth_token("jane.doe@exemple.gouv.fr", token)

        resp = app.get("/authentification", params={"token": token})
        assert resp.status_code == 302
        assert (
            resp.location
            == "https://zam.test/bienvenue?source=https%3A%2F%2Fzam.test%2Flectures%2F"
        )

        user = DBSession.query(User).filter_by(email="jane.doe@exemple.gouv.fr").first()
        assert user.name is None

        resp = resp.follow()
        assert resp.form["name"].value == "Jane Doe"  # prefilled based on email

        resp.form["name"] = " Something Else  "
        resp.form.submit()

        user = DBSession.query(User).filter_by(email="jane.doe@exemple.gouv.fr").first()
        assert user.name == "Something Else"

    def test_new_user_without_name_get_an_error(self, app):
        from zam_repondeur.auth import generate_auth_token
        from zam_repondeur.models import DBSession, User
        from zam_repondeur.users import repository

        user = DBSession.query(User).filter_by(email="jane.doe@exemple.gouv.fr").first()
        assert user is None

        token = generate_auth_token()

        repository.set_auth_token("jane.doe@exemple.gouv.fr", token)

        resp = app.get("/authentification", params={"token": token})
        assert resp.status_code == 302
        assert (
            resp.location
            == "https://zam.test/bienvenue?source=https%3A%2F%2Fzam.test%2Flectures%2F"
        )

        user = DBSession.query(User).filter_by(email="jane.doe@exemple.gouv.fr").first()
        assert user.name is None

        resp = resp.follow()
        assert resp.form["name"].value == "Jane Doe"  # prefilled based on email

        resp.form["name"] = ""
        resp = resp.form.submit()

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/bienvenue"
        resp = resp.follow()
        assert "La saisie d’un nom est requise." in resp.text

        user = DBSession.query(User).filter_by(email="jane.doe@exemple.gouv.fr").first()
        assert user.name is None

    def test_user_with_name_can_edit_it(self, app, user_david):
        from zam_repondeur.models import DBSession, User

        resp = app.get("/bienvenue", user=user_david)
        assert resp.status_code == 200
        assert resp.form["name"].value == "David"
        resp.form["name"] = " Something Else  "
        resp.form.submit()

        user = DBSession.query(User).filter_by(email=user_david.email).first()
        assert user.name == "Something Else"

    def test_user_with_a_name_skips_the_welcome_page(self, app, user_david):
        from zam_repondeur.auth import generate_auth_token
        from zam_repondeur.models import DBSession
        from zam_repondeur.users import repository

        with transaction.manager:
            DBSession.add(user_david)

        assert user_david.name == "David"

        token = generate_auth_token()

        repository.set_auth_token(user_david.email, token)

        resp = app.get("/authentification", params={"token": token})
        assert resp.status_code == 302
        assert resp.location == f"https://zam.test/lectures/"


class TestAuthTokenExpiration:
    def test_can_get_auth_token_before_expiration(self, auth_token):
        from zam_repondeur.users import repository

        assert repository.get_auth_token_data(auth_token) is not None

    def test_cannot_get_auth_token_after_expiration(self, settings, auth_token):
        from zam_repondeur.users import repository

        initial_time = datetime.now(tz=timezone.utc)
        expiration_delay = int(settings["zam.users.auth_token_duration"])
        with freeze_time(initial_time + timedelta(seconds=expiration_delay + 0.01)):
            assert repository.get_auth_token_data(auth_token) is None
