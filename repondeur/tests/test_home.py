import pytest


@pytest.fixture
def app():
    from webtest import TestApp
    from zam_repondeur import make_app

    settings = {}
    wsgi_app = make_app(settings)
    return TestApp(wsgi_app)


def test_home(app):
    resp = app.get("/")
    assert resp.status_code == 200
    assert resp.content_type == "text/html"
    assert "Hello world" in resp.text
