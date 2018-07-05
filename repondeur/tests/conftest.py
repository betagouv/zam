import pytest
import transaction


@pytest.fixture(scope="session")
def settings():
    return {
        "sqlalchemy.url": "sqlite:///test.db",
        "zam.legislature": "15",
        "zam.secret": "dummy",
    }


@pytest.fixture(scope="session")
def wsgi_app(settings):
    from zam_repondeur import make_app

    return make_app(None, **settings)


@pytest.yield_fixture(scope="session", autouse=True)
def use_app_registry(wsgi_app):
    from pyramid.testing import testConfig

    with testConfig(registry=wsgi_app.registry):
        yield


@pytest.yield_fixture
def app(wsgi_app):
    from webtest import TestApp
    from zam_repondeur.models import Base, DBSession

    Base.metadata.drop_all()
    Base.metadata.create_all()

    yield TestApp(wsgi_app)

    Base.metadata.drop_all()
    DBSession.remove()


@pytest.fixture
def dummy_lecture(app):
    from zam_repondeur.models import DBSession, Lecture

    chambre = "an"
    session = "15"
    num_texte = 269
    titre = "Titre lecture"

    with transaction.manager:
        lecture = Lecture(
            chambre=chambre,
            session=session,
            num_texte=num_texte,
            titre=titre,
            organe="PO717460",
        )
        DBSession.add(lecture)

    return (chambre, session, num_texte, titre)


@pytest.fixture
def dummy_amendements(app, dummy_lecture):
    from zam_repondeur.models import DBSession, Amendement

    amendements = []
    for position, num in enumerate((666, 999), 1):
        amendement = Amendement(
            chambre=dummy_lecture[0],
            session=dummy_lecture[1],
            num_texte=dummy_lecture[2],
            subdiv_type="article",
            subdiv_num="1",
            num=num,
            position=position,
        )
        amendements.append(amendement)
    with transaction.manager:
        DBSession.add_all(amendements)

    return amendements
