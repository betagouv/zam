from contextlib import contextmanager

from pyramid.decorator import reify
from selectolax.parser import HTMLParser
from webtest import TestApp as BaseTestApp
from webtest import TestRequest as BaseTestRequest
from webtest import TestResponse as BaseTestResponse


class TestAmendement:
    def __init__(self, amendement, anchor):
        self.amendement = amendement
        self.node = anchor.parent

    def number_is_in_title(self):
        return (
            str(self.amendement.num) in self.node.css_first("header h2").text().strip()
        )

    def has_gouvernemental_class(self):
        return "gouvernemental" in self.node.attributes.get("class")


class TestResponse(BaseTestResponse):
    @reify
    def parser(self):
        return HTMLParser(self.text)

    def first_element(self, name) -> str:
        return self.parser.css_first(name).text()

    def find_amendement(self, amendement):
        anchor = self.parser.css_first(f"#amdt-{amendement.num}")
        if anchor is None:
            return None
        return TestAmendement(amendement, anchor)


class TestRequest(BaseTestRequest):
    ResponseClass = TestResponse


class TestApp(BaseTestApp):
    RequestClass = TestRequest

    def get(self, *args, **kwargs):
        with self.auto_login(kwargs):
            return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        with self.auto_login(kwargs):
            return super().post(*args, **kwargs)

    def post_json(self, *args, **kwargs):
        with self.auto_login(kwargs):
            return super().post_json(*args, **kwargs)

    @contextmanager
    def auto_login(self, kwargs):
        from zam_repondeur.models import User

        user = kwargs.pop("user", None)
        if user is not None:
            assert isinstance(user, User)
            self.user_login(email=user.email, headers=kwargs.get("headers"))

        yield

    def user_login(self, email, headers=None):
        from zam_repondeur.auth import generate_auth_token
        from zam_repondeur.services.users import repository

        token = generate_auth_token()
        repository.set_auth_token(email, token)
        resp = self.get("/authentification", params={"token": token}, headers=headers)
        assert resp.status_code == 302
