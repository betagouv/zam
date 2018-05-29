import pytest


@pytest.fixture
def app():
    from webtest import TestApp
    from zam_repondeur import make_app

    settings = {}
    wsgi_app = make_app(settings)
    return TestApp(wsgi_app)
