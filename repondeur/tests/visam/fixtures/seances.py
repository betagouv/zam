from datetime import date

import pytest
import transaction


@pytest.fixture
def seance_ccfp(db, team_zam):
    from zam_repondeur.models import Chambre
    from zam_repondeur.visam.models import Seance, Formation

    with transaction.manager:
        seance = Seance.create(
            chambre=Chambre.CCFP,
            formation=Formation.ASSEMBLEE_PLENIERE,
            date=date(2020, 4, 1),
        )
        seance.team = team_zam

    return seance


@pytest.fixture
def dossier_seance_ccfp(db, team_zam):
    from zam_repondeur.models import Dossier

    with transaction.manager:
        dossier = Dossier.create(
            an_id="dummy-titre-texte-ccfp",
            titre="Titre du texte CCFP",
            slug="titre-texte-ccfp",
        )
        dossier.team = team_zam

    return dossier


@pytest.fixture
def dossier_seance_ccfp_2(db, team_zam):
    from zam_repondeur.models import Dossier

    with transaction.manager:
        dossier = Dossier.create(
            an_id="dummy-titre-texte-ccfp-2",
            titre="Titre du texte CCFP 2",
            slug="titre-texte-ccfp-2",
        )
        dossier.team = team_zam

    return dossier


@pytest.fixture
def texte_seance_ccfp(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            type_=TypeTexte.PROJET,
            numero=1,
            chambre=Chambre.CCFP,
            date_depot=date(2020, 4, 1),
        )

    return texte


@pytest.fixture
def lecture_seance_ccfp(db, seance_ccfp, dossier_seance_ccfp, texte_seance_ccfp):
    from zam_repondeur.models import DBSession, Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
            texte=texte_seance_ccfp,
            titre="Première lecture – Assemblée plénière",
            organe="Assemblée plénière",
            dossier=dossier_seance_ccfp,
        )
        DBSession.add(seance_ccfp)
        seance_ccfp.lectures.append(lecture)

    return lecture


@pytest.fixture
def article1_texte_seance_ccfp(db, lecture_seance_ccfp):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(lecture=lecture_seance_ccfp, type="article", num="1")

    return article


@pytest.fixture
def amendement_222_lecture_seance_ccfp(
    db, lecture_seance_ccfp, article1_texte_seance_ccfp
):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        amendement = Amendement.create(
            lecture=lecture_seance_ccfp,
            article=article1_texte_seance_ccfp,
            num="v222",
            position=1,
        )

        DBSession.add(amendement)
    return amendement


@pytest.fixture
def amendement_444_lecture_seance_ccfp(
    db, lecture_seance_ccfp, article1_texte_seance_ccfp
):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        amendement = Amendement.create(
            lecture=lecture_seance_ccfp,
            article=article1_texte_seance_ccfp,
            num="v444",
            position=2,
        )

        DBSession.add(amendement)
    return amendement


@pytest.fixture
def lecture_seance_ccfp_2(db, seance_ccfp, dossier_seance_ccfp_2, texte_seance_ccfp):
    from zam_repondeur.models import DBSession, Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
            texte=texte_seance_ccfp,
            titre="Première lecture – Assemblée plénière",
            organe="Assemblée plénière",
            dossier=dossier_seance_ccfp_2,
        )
        DBSession.add(seance_ccfp)
        seance_ccfp.lectures.append(lecture)

    return lecture


@pytest.fixture
def articles_seance_ccfp(db, lecture_seance_ccfp):
    from zam_repondeur.models import Article

    articles = []
    with transaction.manager:
        content = {
            "1": ["Contenu article 1"],
            "2": ["Contenu article 2 alinéa 1", "Contenu article 2 alinéa 2"],
        }
        for num, alineas in content.items():
            article = Article.create(
                type="article",
                num=num,
                mult="",
                pos="",
                lecture=lecture_seance_ccfp,
                content={
                    str(i).zfill(3): alinea for i, alinea in enumerate(alineas, start=1)
                },
            )
            articles.append(article)

    return articles


@pytest.fixture
def seance_csfpe(db, team_zam):
    from zam_repondeur.models import Chambre
    from zam_repondeur.visam.models import Seance, Formation

    with transaction.manager:
        seance = Seance.create(
            chambre=Chambre.CSFPE,
            formation=Formation.ASSEMBLEE_PLENIERE,
            date=date(2020, 5, 15),
        )
        seance.team = team_zam

    return seance


@pytest.fixture
def dossier_seance_csfpe(db, team_zam):
    from zam_repondeur.models import Dossier

    with transaction.manager:
        dossier = Dossier.create(
            an_id="dummy-titre-texte-csfpe",
            titre="Titre du texte CSFPE",
            slug="titre-texte-csfpe",
        )
        dossier.team = team_zam

    return dossier


@pytest.fixture
def texte_seance_csfpe(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            type_=TypeTexte.PROJET,
            numero=2,
            chambre=Chambre.CSFPE,
            date_depot=date(2020, 4, 1),
        )

    return texte


@pytest.fixture
def lecture_seance_csfpe(db, seance_csfpe, dossier_seance_csfpe, texte_seance_csfpe):
    from zam_repondeur.models import DBSession, Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
            texte=texte_seance_csfpe,
            titre="Première lecture – Assemblée plénière",
            organe="Assemblée plénière",
            dossier=dossier_seance_csfpe,
        )
        DBSession.add(seance_csfpe)
        seance_csfpe.lectures.append(lecture)

    return lecture
