import os
from contextlib import contextmanager
from pathlib import Path

import pytest
import responses
import transaction
from pyramid.threadlocal import get_current_registry
from pyramid_mailer import get_mailer

from fixtures.dossiers import *  # noqa: F401,F403
from fixtures.essoc2018 import *  # noqa: F401,F403
from fixtures.lectures import *  # noqa: F401,F403
from fixtures.organes_acteurs import *  # noqa: F401,F403
from fixtures.plf2018 import *  # noqa: F401,F403
from fixtures.plfss2018 import *  # noqa: F401,F403
from fixtures.plfss2019 import *  # noqa: F401,F403
from fixtures.scraping import *  # noqa: F401,F403
from fixtures.shared_tables import *  # noqa: F401,F403
from fixtures.users import *  # noqa: F401,F403
from testapp import TestApp as BaseTestApp

HERE = Path(__file__)


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
        from zam_repondeur.auth import generate_auth_token
        from zam_repondeur.services.users import repository

        token = generate_auth_token()
        repository.set_auth_token(email, token)
        resp = self.get("/authentification", params={"token": token}, headers=headers)
        assert resp.status_code == 302


@pytest.fixture(scope="session")
def settings(tmp_path_factory):
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
        "zam.users.max_token_requests_per_email_per_minute": "5",
        "zam.users.max_token_requests_per_ip_per_minute": "10",
        "zam.users.max_token_validations_per_ip_per_minute": "10",
        "zam.amendements.redis_url": os.environ.get(
            "ZAM_TEST_AMENDEMENTS_REDIS_URL", "redis://localhost:6379/13"
        ),
        "zam.progress.redis_url": os.environ.get(
            "ZAM_TEST_PROGRESS_REDIS_URL", "redis://localhost:6379/14"
        ),
        "zam.progress.max_duration": os.environ.get(
            "ZAM_TEST_PROGRESS_MAX_DURATION", "1"  # minutes.
        ),
        "zam.session_secret": "dummy",
        "zam.auth_secret": "dummier",
        "zam.auth_admins": ["user@sgg.pm.gouv.fr"],
        # Only wait for 1 second to speed up integration tests.
        "zam.check_for.amendement_stolen_while_editing": 1,
        "zam.check_for.transfers_from_to_my_table": 1,
        # Minutes
        "zam.http_cache_duration": 0,
        "zam.http_cache_dir": str(tmp_path_factory.mktemp(".web_cache")),
    }


@pytest.fixture(scope="session")  # noqa: F811
def wsgi_app(settings, mock_dossiers, mock_organes_acteurs, mock_scraping_senat):
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


@pytest.fixture(autouse=True)
def run_each_test_in_a_fresh_new_transaction():
    with transaction.manager:
        yield
        transaction.abort()  # rollback


@pytest.fixture(scope="session")
@responses.activate
def data_repository():
    from zam_repondeur.services.data import repository

    SENAT_SAMPLE_DATA_DIR = HERE.parent / "fetch" / "sample_data" / "senat"
    responses.add(
        responses.GET,
        "https://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv",
        body=(SENAT_SAMPLE_DATA_DIR / "ODSEN_GENERAL.csv").read_bytes(),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://www.senat.fr/dossiers-legislatifs/textes-recents.html",
        body=(SENAT_SAMPLE_DATA_DIR / "textes-recents.html").read_bytes(),
        status=200,
    )
    for path in SENAT_SAMPLE_DATA_DIR.glob("dosleg*.xml"):
        responses.add(
            responses.GET,
            f"https://www.senat.fr/dossier-legislatif/rss/{path.name}",
            body=path.read_bytes(),
            status=200,
        )
    repository.load_data()


@pytest.fixture
def users_repository():
    from zam_repondeur.services.users import repository

    repository.clear_data()

    yield

    repository.clear_data()


@pytest.fixture
def amendements_repository():
    from zam_repondeur.services.amendements import repository

    repository.clear_data()

    yield

    repository.clear_data()


@pytest.fixture
def progress_repository():
    from zam_repondeur.services.progress import repository

    repository.clear_data()

    yield

    repository.clear_data()


@pytest.fixture()
def whitelist(db):
    from zam_repondeur.models.users import AllowedEmailPattern

    with transaction.manager:
        allowed_email_pattern = AllowedEmailPattern.create(pattern="*@*.gouv.fr")

    return allowed_email_pattern


@pytest.fixture
def app(
    wsgi_app,
    db,
    whitelist,
    data_repository,
    users_repository,
    amendements_repository,
    progress_repository,
):
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
    This hook is called by pytest before running each test (after fixtures / setup)

    See: https://docs.pytest.org/en/latest/reference.html#hook-reference
    """
    clear_email_outbox()
    clear_rate_limiting_counters()


def clear_email_outbox():
    registry = get_current_registry()
    mailer = get_mailer(registry)
    mailer.outbox = []


def clear_rate_limiting_counters():
    """
    This prevents throttling caused by the many logins from automatic tests
    """
    from zam_repondeur.services.users import repository

    redis = repository.connection
    keys = redis.keys("rate-limiter:*")
    if keys:
        redis.delete(*keys)
