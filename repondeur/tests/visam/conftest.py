import pytest

from testapp import TestApp


@pytest.fixture(scope="session")  # noqa: F811
def wsgi_app(settings, mock_dossiers, mock_organes_acteurs, mock_scraping_senat):
    from zam_repondeur.visam.app import make_app

    return make_app(None, **settings)


@pytest.fixture
def app(
    wsgi_app, db, whitelist, data_repository, users_repository,
):
    yield TestApp(
        wsgi_app,
        extra_environ={
            "HTTP_HOST": "visam.test",
            "REMOTE_ADDR": "127.0.0.1",
            "wsgi.url_scheme": "https",
        },
    )
