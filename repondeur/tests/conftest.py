import pytest
import transaction

from fixtures.dossiers import mock_dossiers  # noqa: F401
from fixtures.organes_acteurs import mock_organes_acteurs  # noqa: F401
from testapp import TestApp


@pytest.fixture(scope="session")
def settings():
    return {
        "sqlalchemy.url": "sqlite:///test.db",
        "zam.legislature": "15",
        "zam.secret": "dummy",
        "jinja2.filters": "paragriphy = zam_repondeur.views.jinja2_filters:paragriphy",
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


@pytest.yield_fixture
def app(wsgi_app):
    from zam_repondeur.models import Base, DBSession

    Base.metadata.drop_all()
    Base.metadata.create_all()

    yield TestApp(wsgi_app)

    DBSession.close()
    Base.metadata.drop_all()
    DBSession.remove()


@pytest.fixture
def dummy_lecture(app):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            num_texte=269,
            titre="Titre lecture",
            organe="PO717460",
            dossier_legislatif="Titre dossier legislatif",
        )

    return lecture


@pytest.fixture
def dummy_amendements(app, dummy_lecture):
    from zam_repondeur.models import DBSession, Amendement

    with transaction.manager:
        amendements = [
            Amendement(
                chambre=dummy_lecture.chambre,
                session=dummy_lecture.session,
                num_texte=dummy_lecture.num_texte,
                organe=dummy_lecture.organe,
                subdiv_type="article",
                subdiv_num="1",
                num=num,
                position=position,
            )
            for position, num in enumerate((666, 999), 1)
        ]
        DBSession.add_all(amendements)

    return amendements


@pytest.fixture
def dummy_amendements_with_reponses(app, dummy_lecture):
    from zam_repondeur.models import DBSession, Amendement

    with transaction.manager:
        amendements = [
            Amendement(
                chambre=dummy_lecture.chambre,
                session=dummy_lecture.session,
                num_texte=dummy_lecture.num_texte,
                organe=dummy_lecture.organe,
                subdiv_type="article",
                subdiv_num="1",
                num=num,
                position=position,
                avis="Favorable",
                observations="Des observations très pertinentes",
                reponse="Une réponse très appropriée",
                comments="Avec des commentaires",
            )
            for position, num in enumerate((333, 777), 1)
        ]
        DBSession.add_all(amendements)

    return amendements
