import os
from contextlib import contextmanager

import pytest

from fixtures.dossiers import mock_dossiers  # noqa: F401
from fixtures.organes_acteurs import mock_organes_acteurs  # noqa: F401
from fixtures.lectures import *  # noqa: F401,F403
from fixtures.users import *  # noqa: F401,F403
from testapp import TestApp as BaseTestApp


class TestApp(BaseTestApp):
    def get(self, *args, **kwargs):
        with self.auto_login(kwargs):
            return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        with self.auto_login(kwargs):
            return super().post(*args, **kwargs)

    @contextmanager
    def auto_login(self, kwargs):
        from zam_repondeur.models import User

        user = kwargs.pop("user", None)
        if user is not None:
            assert isinstance(user, User)
            self.user_login(email=user.email, headers=kwargs.get("headers"))

        yield

    def user_login(self, email, headers=None):
        resp = self.post("/identification", {"email": email}, headers=headers)
        assert resp.status_code == 302


@pytest.fixture(scope="session")
def settings():
    return {
        "pyramid.debug_authorization": True,
        "sqlalchemy.url": os.environ.get(
            "ZAM_TEST_DB_URL", "postgresql://zam@localhost/zam-test"
        ),
        "zam.tasks.redis_url": os.environ.get(
            "ZAM_TEST_TASKS_REDIS_URL", "redis://localhost:6379/10"
        ),
        "zam.tasks.always_eager": True,
        "zam.data.redis_url": os.environ.get(
            "ZAM_TEST_DATA_REDIS_URL", "redis://localhost:6379/11"
        ),
        "zam.users.redis_url": os.environ.get(
            "ZAM_TEST_USERS_REDIS_URL", "redis://localhost:6379/12"
        ),
        "zam.session_secret": "dummy",
        "zam.auth_secret": "dummier",
    }


@pytest.fixture(scope="session")  # noqa: F811
def wsgi_app(settings, mock_dossiers, mock_organes_acteurs):
    from zam_repondeur import make_app

    return make_app(None, **settings)


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


@pytest.fixture
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
def app(wsgi_app, db, data_repository, users_repository):
    yield TestApp(
        wsgi_app, extra_environ={"HTTP_HOST": "zam.test", "wsgi.url_scheme": "https"}
    )
