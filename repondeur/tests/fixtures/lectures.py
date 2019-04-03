from datetime import datetime

import pytest
import transaction


@pytest.fixture
def texte_an(db):
    from zam_repondeur.models import Texte

    with transaction.manager:
        texte = Texte.create(
            uid="PRJLANR5L15B0269",
            type_="Projet de loi",
            numero=269,
            titre_long="projet de loi de financement de la sécurité sociale pour 2018",
            titre_court="PLFSS pour 2018",
            date_depot=datetime(2017, 10, 11),
        )

    return texte


@pytest.fixture
def texte_commission_speciale(db):
    from zam_repondeur.models import Texte

    with transaction.manager:
        texte = Texte.create(
            uid="PRJLANR5L15B0806",
            type_="Projet de loi",
            numero=806,
            titre_long="long",
            titre_court="court",
            date_depot=datetime(2017, 10, 11),
        )

    return texte


@pytest.fixture
def dossier_an(db):
    from zam_repondeur.models import Dossier

    with transaction.manager:
        texte = Dossier.create(uid="foo", titre="Titre dossier legislatif AN")

    return texte


@pytest.fixture
def lecture_an(db, texte_an, dossier_an):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            texte=texte_an,
            titre="Numéro lecture – Titre lecture",
            organe="PO717460",
            dossier=dossier_an,
        )

    return lecture


@pytest.fixture
def texte_senat(db):
    from zam_repondeur.models import Texte

    with transaction.manager:
        texte = Texte.create(
            uid="baz",
            type_="Projet de loi",
            numero=63,
            titre_long="long",
            titre_court="court",
            date_depot=datetime(2017, 10, 11),
        )

    return texte


@pytest.fixture
def dossier_senat(db):
    from zam_repondeur.models import Dossier

    with transaction.manager:
        texte = Dossier.create(uid="bar", titre="Titre dossier legislatif sénat")

    return texte


@pytest.fixture
def lecture_senat(db, texte_senat, dossier_senat):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="senat",
            session="2017-2018",
            texte=texte_senat,
            titre="Numéro lecture – Titre lecture sénat",
            organe="PO78718",
            dossier=dossier_senat,
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
def texte_essoc(db):
    from zam_repondeur.models import Texte

    with transaction.manager:
        texte = Texte.create(
            uid="PRJLANR5L15B0806",
            type_="Projet de loi",
            numero=806,
            titre_long="long",
            titre_court="court",
            date_depot=datetime(2017, 10, 11),
        )

    return texte


@pytest.fixture
def dossier_essoc(db):
    from zam_repondeur.models import Dossier

    with transaction.manager:
        texte = Dossier.create(
            uid="bar",
            titre="Fonction publique : un Etat au service d'une société de confiance",
        )

    return texte


@pytest.fixture
def lecture_essoc(db, texte_essoc, dossier_essoc):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            texte=texte_essoc,
            titre="Nouvelle lecture – Titre lecture",
            organe="PO744107",
            dossier=dossier_essoc,
        )

    return lecture
