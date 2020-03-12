from copy import deepcopy

import pytest


@pytest.fixture(scope="session")
def settings(settings):
    visam_settings = deepcopy(settings)
    visam_settings["pyramid.includes"].append("zam_repondeur.visam")
    return visam_settings


@pytest.fixture(scope="session")  # noqa: F811
def wsgi_app(settings, mock_dossiers, mock_organes_acteurs, mock_scraping_senat):
    from zam_repondeur import make_app

    return make_app(None, **settings)
