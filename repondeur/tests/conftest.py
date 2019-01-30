import os

import pytest
import transaction

from fixtures.dossiers import mock_dossiers  # noqa: F401
from fixtures.organes_acteurs import mock_organes_acteurs  # noqa: F401
from testapp import TestApp as BaseTestApp


class TestApp(BaseTestApp):
    def login(self, email):
        resp = self.post("/identification", {"email": email})
        assert resp.status_code == 302

    def get(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        if user is not None:
            self.login(user)
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        if user is not None:
            self.login(user)
        return super().post(*args, **kwargs)


@pytest.fixture(scope="session")
def settings():
    return {
        "sqlalchemy.url": os.environ.get(
            "ZAM_TEST_DB_URL", "postgresql://zam@localhost/zam-test"
        ),
        "zam.tasks.redis_url": os.environ.get(
            "ZAM_TEST_TASKS_REDIS_URL", "redis://localhost:6379/10"
        ),
        "zam.tasks.always_eager": True,
        "zam.data.redis_url": os.environ.get(
            "ZAM_TEST_DATA_REDIS_URL", "redis://localhost:6379/11"
        ),
        "zam.session_secret": "dummy",
        "zam.auth_secret": "dummier",
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


@pytest.fixture
def db():
    from zam_repondeur.models import Base, DBSession

    Base.metadata.drop_all()
    Base.metadata.create_all()

    yield DBSession

    DBSession.close()
    Base.metadata.drop_all()
    DBSession.remove()


@pytest.fixture
def data_repository():
    from zam_repondeur.data import _repository

    _repository.clear_data()
    _repository.load_data()

    yield

    _repository.clear_data()


@pytest.fixture
def app(wsgi_app, db, data_repository):
    yield TestApp(
        wsgi_app, extra_environ={"HTTP_HOST": "zam.test", "wsgi.url_scheme": "https"}
    )


@pytest.fixture
def user_david(db):
    from zam_repondeur.models import User

    return User.create(name="David", email="david@example.com")


@pytest.fixture
def lecture_an(db):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            num_texte=269,
            titre="Numéro lecture – Titre lecture",
            organe="PO717460",
            dossier_legislatif="Titre dossier legislatif",
        )

    return lecture


@pytest.fixture
def lecture_senat(db):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="senat",
            session="2017-2018",
            num_texte=63,
            titre="Numéro lecture – Titre lecture sénat",
            organe="PO78718",
            dossier_legislatif="Titre dossier legislatif sénat",
        )

    return lecture


@pytest.fixture
def chapitre_1er_an(db, lecture_an):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(lecture=lecture_an, type="chapitre", num="Ier")

    return article


@pytest.fixture
def article1_an(db, lecture_an):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(lecture=lecture_an, type="article", num="1")

    return article


@pytest.fixture
def article1av_an(db, lecture_an):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(
            lecture=lecture_an, type="article", num="1", pos="avant"
        )

    return article


@pytest.fixture
def article7bis_an(db, lecture_an):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(
            lecture=lecture_an, type="article", num="7", mult="bis"
        )

    return article


@pytest.fixture
def annexe_an(db, lecture_an):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(lecture=lecture_an, type="annexe")

    return article


@pytest.fixture
def article1_senat(db, lecture_senat):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(lecture=lecture_senat, type="article", num="1")

    return article


@pytest.fixture
def article1av_senat(db, lecture_senat):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(
            lecture=lecture_senat, type="article", num="1", pos="avant"
        )

    return article


@pytest.fixture
def article7bis_senat(db, lecture_senat):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(
            lecture=lecture_senat, type="article", num="7", mult="bis"
        )

    return article


@pytest.fixture
def amendements_an(db, lecture_an, article1_an):
    from zam_repondeur.models import Amendement

    with transaction.manager:
        amendements = [
            Amendement.create(
                lecture=lecture_an, article=article1_an, num=num, position=position
            )
            for position, num in enumerate((666, 999), 1)
        ]

    return amendements


@pytest.fixture
def amendements_senat(db, lecture_senat, article1_senat):
    from zam_repondeur.models import Amendement

    with transaction.manager:
        amendements = [
            Amendement.create(
                lecture=lecture_senat,
                article=article1_senat,
                num=num,
                position=position,
            )
            for position, num in enumerate((6666, 9999), 1)
        ]

    return amendements


@pytest.fixture
def lecture_essoc(db):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            num_texte=806,
            titre="Nouvelle lecture – Titre lecture",
            organe="PO744107",
            dossier_legislatif="Fonction publique : un Etat au service d'une société de confiance",  # noqa
        )

    return lecture
