import pytest
import transaction


@pytest.yield_fixture
def app():
    from webtest import TestApp
    from zam_repondeur import make_app
    from zam_repondeur.models import Base, DBSession

    settings = {"sqlalchemy.url": "sqlite:///test.db", "zam.secret": "dummy"}
    wsgi_app = make_app(None, **settings)

    Base.metadata.drop_all()
    Base.metadata.create_all()

    yield TestApp(wsgi_app)

    Base.metadata.drop_all()
    DBSession.remove()


@pytest.fixture
def dummy_lecture(app):
    from zam_repondeur.models import DBSession, Lecture

    with transaction.manager:
        lecture = Lecture(chambre="an", session="15", num_texte="0269")
        DBSession.add(lecture)

    return lecture
