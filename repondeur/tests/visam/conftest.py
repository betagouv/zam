import pytest


@pytest.fixture(scope="session")  # noqa: F811
def wsgi_app(settings, mock_dossiers, mock_organes_acteurs, mock_scraping_senat):
    from zam_repondeur.visam.app import make_app

    return make_app(None, **settings)
