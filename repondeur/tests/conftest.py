import pytest


@pytest.fixture
def app(tmpdir):
    from webtest import TestApp
    from zam_repondeur import make_app

    settings = {"zam.data_dir": str(tmpdir.mkdir("zam"))}
    wsgi_app = make_app(None, **settings)
    return TestApp(wsgi_app)
