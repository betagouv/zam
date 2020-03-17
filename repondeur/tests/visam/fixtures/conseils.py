from datetime import date

import pytest
import transaction


@pytest.fixture
def conseil_ccfp(db, team_zam):
    from zam_repondeur.models import Chambre
    from zam_repondeur.visam.models import Conseil, Formation

    with transaction.manager:
        conseil = Conseil.create(
            chambre=Chambre.CCFP,
            formation=Formation.ASSEMBLEE_PLENIERE,
            date=date(2020, 4, 1),
        )
        conseil.team = team_zam

    return conseil


@pytest.fixture
def dossier_conseil_ccfp(db, team_zam):
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
def texte_conseil_ccfp(db):
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
def lecture_conseil_ccfp(db, conseil_ccfp, dossier_conseil_ccfp, texte_conseil_ccfp):
    from zam_repondeur.models import DBSession, Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
            texte=texte_conseil_ccfp,
            titre="Première lecture – Assemblée plénière",
            organe="Assemblée plénière",
            dossier=dossier_conseil_ccfp,
        )
        DBSession.add(conseil_ccfp)
        conseil_ccfp.lectures.append(lecture)

    return lecture


@pytest.fixture
def conseil_csfpe(db, team_zam):
    from zam_repondeur.models import Chambre
    from zam_repondeur.visam.models import Conseil, Formation

    with transaction.manager:
        conseil = Conseil.create(
            chambre=Chambre.CSFPE,
            formation=Formation.ASSEMBLEE_PLENIERE,
            date=date(2020, 4, 1),
        )
        conseil.team = team_zam

    return conseil


@pytest.fixture
def dossier_conseil_csfpe(db, team_zam):
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
def texte_conseil_csfpe(db):
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
def lecture_conseil_csfpe(
    db, conseil_csfpe, dossier_conseil_csfpe, texte_conseil_csfpe
):
    from zam_repondeur.models import DBSession, Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
            texte=texte_conseil_csfpe,
            titre="Première lecture – Assemblée plénière",
            organe="Assemblée plénière",
            dossier=dossier_conseil_csfpe,
        )
        DBSession.add(conseil_csfpe)
        conseil_csfpe.lectures.append(lecture)

    return lecture
