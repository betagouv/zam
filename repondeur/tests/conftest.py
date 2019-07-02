import os
from contextlib import contextmanager

import pytest
from pyramid.threadlocal import get_current_registry
from pyramid_mailer import get_mailer

from fixtures.dossiers import *  # noqa: F401,F403
from fixtures.organes_acteurs import *  # noqa: F401,F403
from fixtures.lectures import *  # noqa: F401,F403
from fixtures.essoc2018 import *  # noqa: F401,F403
from fixtures.plf2018 import *  # noqa: F401,F403
from fixtures.plfss2018 import *  # noqa: F401,F403
from fixtures.scraping import *  # noqa: F401,F403
from fixtures.users import *  # noqa: F401,F403
from testapp import TestApp as BaseTestApp

from zam_repondeur.auth import generate_auth_token
from zam_repondeur.users import repository


class TestApp(BaseTestApp):
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
        token = generate_auth_token()
        repository.set_auth_token(email, token)
        resp = self.get("/authentification", params={"token": token}, headers=headers)
        assert resp.status_code == 302


@pytest.fixture(scope="session")
def settings():
    return {
        "pyramid.debug_authorization": True,
        "pyramid.includes": "pyramid_mailer.testing",
        "sqlalchemy.url": os.environ.get(
            "ZAM_TEST_DB_URL", "postgresql://zam@localhost/zam-test"
        ),
        "zam.tasks.redis_url": os.environ.get(
            "ZAM_TEST_TASKS_REDIS_URL", "redis://localhost:6379/10"
        ),
        "zam.tasks.immediate": True,
        "zam.data.redis_url": os.environ.get(
            "ZAM_TEST_DATA_REDIS_URL", "redis://localhost:6379/11"
        ),
        "zam.users.redis_url": os.environ.get(
            "ZAM_TEST_USERS_REDIS_URL", "redis://localhost:6379/12"
        ),
        "zam.users.auth_token_duration": "60",
        "zam.amendements.redis_url": os.environ.get(
            "ZAM_TEST_AMENDEMENTS_REDIS_URL", "redis://localhost:6379/13"
        ),
        "zam.session_secret": "dummy",
        "zam.auth_secret": "dummier",
        # Only wait for 1 second to speed up integration tests.
        "zam.check_for.amendement_stolen_while_editing": 1,
        "zam.check_for.transfers_from_to_my_table": 1,
    }


@pytest.fixture(scope="session")  # noqa: F811
def wsgi_app(settings, mock_dossiers, mock_organes_acteurs, mock_scraping_senat):
    from zam_repondeur import make_app

    app = make_app(None, **settings)
    app.settings = settings
    return app


@pytest.yield_fixture(scope="session", autouse=True)
def use_app_registry(wsgi_app):
    from pyramid.testing import testConfig

    with testConfig(registry=wsgi_app.registry):
        yield


@pytest.fixture
def db():
    from zam_repondeur.models import Base, DBSession

    Base.metadata.drop_all()
    Base.metadata.create_all()

    yield DBSession

    DBSession.close()
    Base.metadata.drop_all()
    DBSession.remove()


@pytest.fixture(scope="session")
def data_repository():
    from zam_repondeur.data import repository

    repository.load_data()


@pytest.fixture
def users_repository():
    from zam_repondeur.users import repository

    repository.clear_data()

    yield

    repository.clear_data()


@pytest.fixture
def amendements_repository():
    from zam_repondeur.amendements import repository

    repository.clear_data()

    yield

    repository.clear_data()


@pytest.fixture
def app(wsgi_app, db, data_repository, users_repository, amendements_repository):
    yield TestApp(
        wsgi_app,
        extra_environ={
            "HTTP_HOST": "zam.test",
            "REMOTE_ADDR": "127.0.0.1",
            "wsgi.url_scheme": "https",
        },
    )


@pytest.fixture
def mailer():
    registry = get_current_registry()
    yield get_mailer(registry)


def pytest_runtest_call(item):
    """
    Clear e-mail outbox before each test

    This hook is called by pytest before running each test (after fixtures / setup)

    See: https://docs.pytest.org/en/latest/reference.html#hook-reference
    """
    registry = get_current_registry()
    mailer = get_mailer(registry)
    mailer.outbox = []
