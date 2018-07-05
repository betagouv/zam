from datetime import date
from unittest.mock import patch

import pytest
import transaction

from testapp import TestApp


@pytest.fixture(scope="session")
def settings():
    return {
        "sqlalchemy.url": "sqlite:///test.db",
        "zam.legislature": "15",
        "zam.secret": "dummy",
    }


@pytest.yield_fixture(scope="session", autouse=True)
def mock_dossiers():
    from zam_aspirateur.textes.models import Chambre, Dossier, Lecture, Texte, TypeTexte

    with patch("zam_repondeur.data.get_dossiers_legislatifs") as m_dossiers:
        m_dossiers.return_value = {
            "DLR5L15N36030": Dossier(
                uid="DLR5L15N36030",
                titre="Sécurité sociale : loi de financement 2018",
                lectures=[
                    Lecture(
                        chambre=Chambre.AN,
                        titre="1ère lecture",
                        texte=Texte(
                            uid="PRJLANR5L15B0269",
                            type_=TypeTexte.PROJET,
                            numero=269,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 10, 11),
                        ),
                        organe="PO717460",
                    )
                ],
            )
        }
        yield


@pytest.yield_fixture(scope="session", autouse=True)
def mock_organes():
    with patch("zam_repondeur.data.get_organes") as m_organes:
        m_organes.return_value = {
            "PO59048": {
                "@xsi:type": "OrganeParlementaire_Type",
                "uid": "PO59048",
                "codeType": "COMPER",
                "libelle": "Commission des finances, de l'économie générale et du contrôle budgétaire",  # noqa
                "libelleEdition": "de la commission des finances",
                "libelleAbrege": "Finances",
                "libelleAbrev": "CION_FIN",
                "viMoDe": {
                    "dateDebut": "1958-12-09",
                    "dateAgrement": None,
                    "dateFin": None,
                },
                "organeParent": None,
                "chambre": None,
                "regime": "5ème République",
                "legislature": None,
                "secretariat": {
                    "secretaire01": "Mme Dominique Meunier-Ferry",
                    "secretaire02": None,
                },
            },
            "PO717460": {
                "@xsi:type": "OrganeParlementaire_Type",
                "uid": "PO717460",
                "codeType": "ASSEMBLEE",
                "libelle": "Assemblée nationale de la 15ème législature",
                "libelleEdition": "de l'Assemblée",
                "libelleAbrege": "Assemblée",
                "libelleAbrev": "AN",
                "viMoDe": {
                    "dateDebut": "2017-06-21",
                    "dateAgrement": None,
                    "dateFin": None,
                },
                "organeParent": None,
                "chambre": None,
                "regime": "5ème République",
                "legislature": "15",
                "secretariat": {"secretaire01": None, "secretaire02": None},
            },
            "PO78718": {
                "@xsi:type": "OrganeExterne_Type",
                "uid": "PO78718",
                "codeType": "SENAT",
                "libelle": "Sénat ( 5ème République )",
                "libelleEdition": "du sénat ( 5ème République )",
                "libelleAbrege": "Sénat",
                "libelleAbrev": "SENAT",
                "viMoDe": {
                    "dateDebut": "1958-12-09",
                    "dateAgrement": None,
                    "dateFin": None,
                },
                "organeParent": None,
            },
        }
        yield


@pytest.fixture(scope="session")
def wsgi_app(settings, mock_dossiers, mock_organes):
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
    from zam_repondeur.models import DBSession, Lecture

    with transaction.manager:
        lecture = Lecture(
            chambre="an",
            session="15",
            num_texte=269,
            titre="Titre lecture",
            organe="PO717460",
        )
        DBSession.add(lecture)

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
                subdiv_type="article",
                subdiv_num="1",
                num=num,
                position=position,
            )
            for position, num in enumerate((666, 999), 1)
        ]
        DBSession.add_all(amendements)

    return amendements
