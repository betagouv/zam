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
        "huey.always_eager": True,
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
def lecture_an(app):
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
def lecture_senat(app):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="senat",
            session="2017-2018",
            num_texte=63,
            titre="Titre lecture sénat",
            organe="PO78718",
            dossier_legislatif="Titre dossier legislatif sénat",
        )

    return lecture


@pytest.fixture
def article1_an(app, lecture_an):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(lecture=lecture_an, type="article", num="1")

    return article


@pytest.fixture
def article1av_an(app, lecture_an):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(
            lecture=lecture_an, type="article", num="1", pos="avant"
        )

    return article


@pytest.fixture
def article7bis_an(app, lecture_an):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(
            lecture=lecture_an, type="article", num="7", mult="bis"
        )

    return article


@pytest.fixture
def annexe_an(app, lecture_an):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(lecture=lecture_an, type="annexe")

    return article


@pytest.fixture
def article1_senat(app, lecture_senat):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(lecture=lecture_senat, type="article", num="1")

    return article


@pytest.fixture
def article1av_senat(app, lecture_senat):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(
            lecture=lecture_senat, type="article", num="1", pos="avant"
        )

    return article


@pytest.fixture
def article7bis_senat(app, lecture_senat):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(
            lecture=lecture_senat, type="article", num="7", mult="bis"
        )

    return article


@pytest.fixture
def amendements_an(app, lecture_an, article1_an):
    from zam_repondeur.models import DBSession, Amendement

    with transaction.manager:
        amendements = [
            Amendement(
                lecture=lecture_an, article=article1_an, num=num, position=position
            )
            for position, num in enumerate((666, 999), 1)
        ]
        DBSession.add_all(amendements)

    return amendements


@pytest.fixture
def amendements_senat(app, lecture_senat, article1_senat):
    from zam_repondeur.models import DBSession, Amendement

    with transaction.manager:
        amendements = [
            Amendement(
                lecture=lecture_senat,
                article=article1_senat,
                num=num,
                position=position,
            )
            for position, num in enumerate((6666, 9999), 1)
        ]
        DBSession.add_all(amendements)

    return amendements
