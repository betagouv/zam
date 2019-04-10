import time

import pytest
import transaction


def test_unauthentified_user_can_view_login_page(app):
    resp = app.get("/identification")
    assert resp.status_code == 200


def test_user_gets_an_auth_cookie_after_identifying_herself(app):
    assert "auth_tkt" not in app.cookies  # no auth cookie yet

    resp = app.post("/identification", {"email": "jane.doe@example.com"})

    assert resp.status_code == 302
    assert (
        resp.location
        == "https://zam.test/bienvenue?source=https%3A%2F%2Fzam.test%2Flectures%2F"
    )

    assert "auth_tkt" in app.cookies  # and now we have the auth cookie

    domains = {cookie.domain for cookie in app.cookiejar}
    assert domains == {".zam.test", "zam.test"}

    for cookie in app.cookiejar:
        assert cookie.name == "auth_tkt"
        assert cookie.path == "/"
        assert cookie.secure is True

        # Auth cookie should expire after 7 days
        assert cookie.expires == int(time.time()) + (7 * 24 * 3600)

        # We want users to be able to follow an e-mailed link to the app
        # (see: https://www.owasp.org/index.php/SameSite)
        assert cookie.get_nonstandard_attr("SameSite") == "Lax"


def test_user_must_authenticate_with_an_email(app):
    resp = app.post("/identification", {"email": ""})

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/identification"
    resp = resp.follow()
    assert "La saisie d’une adresse de courriel est requise." in resp.text


@pytest.mark.parametrize("incorrect_email", [" ", "foo"])
def test_user_must_authenticate_with_a_valid_email(app, incorrect_email):
    resp = app.post("/identification", {"email": incorrect_email})

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/identification"
    resp = resp.follow()
    assert "La saisie d’une adresse de courriel valide est requise." in resp.text


def test_user_loses_the_auth_cookie_when_loggin_out(app):
    app.post("/identification", {"email": "jane.doe@example.com"})
    assert "auth_tkt" in app.cookies  # the auth cookie is set

    app.get("/deconnexion")
    assert "auth_tkt" not in app.cookies  # the auth cookie is gone


def test_unauthentified_user_is_redirected_to_login_page(app):
    resp = app.get("/lectures/add")
    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test/identification"
        "?source=https%3A%2F%2Fzam.test%2Flectures%2Fadd"
    )


def test_authentified_user_is_not_redirected_to_login_page(app, user_david):
    resp = app.get("/lectures/add", user=user_david)
    assert resp.status_code == 200


def test_new_user_must_enter_their_name_on_the_welcome_page(app):
    from zam_repondeur.models import DBSession, User

    user = DBSession.query(User).filter_by(email="jane.doe@example.com").first()
    assert user is None

    resp = app.post("/identification", {"email": "jane.doe@example.com"})
    assert resp.status_code == 302
    assert (
        resp.location
        == "https://zam.test/bienvenue?source=https%3A%2F%2Fzam.test%2Flectures%2F"
    )

    user = DBSession.query(User).filter_by(email="jane.doe@example.com").first()
    assert user.name is None

    resp = resp.follow()
    assert resp.form["name"].value == "Jane Doe"  # prefilled based on email

    resp.form["name"] = " Something Else  "
    resp.form.submit()

    user = DBSession.query(User).filter_by(email="jane.doe@example.com").first()
    assert user.name == "Something Else"


def test_new_user_without_name_get_an_error(app):
    from zam_repondeur.models import DBSession, User

    user = DBSession.query(User).filter_by(email="jane.doe@example.com").first()
    assert user is None

    resp = app.post("/identification", {"email": "jane.doe@example.com"})
    assert resp.status_code == 302
    assert (
        resp.location
        == "https://zam.test/bienvenue?source=https%3A%2F%2Fzam.test%2Flectures%2F"
    )

    user = DBSession.query(User).filter_by(email="jane.doe@example.com").first()
    assert user.name is None

    resp = resp.follow()
    assert resp.form["name"].value == "Jane Doe"  # prefilled based on email

    resp.form["name"] = ""
    resp = resp.form.submit()

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/bienvenue"
    resp = resp.follow()
    assert "La saisie d’un nom est requise." in resp.text

    user = DBSession.query(User).filter_by(email="jane.doe@example.com").first()
    assert user.name is None


def test_user_with_name_can_edit_it(app, user_david):
    from zam_repondeur.models import DBSession, User

    resp = app.get("/bienvenue", user=user_david)
    assert resp.status_code == 200
    assert resp.form["name"].value == "David"
    resp.form["name"] = " Something Else  "
    resp.form.submit()

    user = DBSession.query(User).filter_by(email=user_david.email).first()
    assert user.name == "Something Else"


def test_user_with_a_name_skips_the_welcome_page(app, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david)

    assert user_david.name == "David"

    resp = app.post("/identification", {"email": "david@example.com"})
    assert resp.status_code == 302
    assert resp.location == f"https://zam.test/lectures/"
