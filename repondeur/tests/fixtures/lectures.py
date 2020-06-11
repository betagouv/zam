import pytest
import transaction


@pytest.fixture
def lecture_an(db, dossier_plfss2018, texte_plfss2018_an_premiere_lecture):
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
            texte=texte_plfss2018_an_premiere_lecture,
            titre="Numéro lecture – Titre lecture",
            organe="PO717460",
            dossier=dossier_plfss2018,
        )

    return lecture


@pytest.fixture
def lecture_an_url(lecture_an):
    return "/dossiers/plfss-2018/lectures/an.15.269.PO717460"


@pytest.fixture
def lecture_senat(db, dossier_plfss2018, texte_plfss2018_senat_premiere_lecture):
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
            texte=texte_plfss2018_senat_premiere_lecture,
            titre="Numéro lecture – Titre lecture sénat",
            organe="PO78718",
            dossier=dossier_plfss2018,
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
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        amendements = [
            Amendement.create(
                lecture=lecture_an, article=article1_an, num=num, position=position
            )
            for position, num in enumerate((666, 999), 1)
        ]

    DBSession.add_all(amendements)
    return amendements


@pytest.fixture
def amendements_an_batch(amendements_an):
    from zam_repondeur.models import Batch, DBSession

    with transaction.manager:
        batch = Batch.create()
        amendements_an[0].location.batch = batch
        amendements_an[1].location.batch = batch
        DBSession.add_all(amendements_an)

    return amendements_an


@pytest.fixture
def amendements_senat(db, lecture_senat, article1_senat):
    from zam_repondeur.models import Amendement, DBSession

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

    DBSession.add_all(amendements)
    return amendements
