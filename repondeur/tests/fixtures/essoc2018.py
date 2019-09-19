from datetime import date

import pytest
import transaction


@pytest.fixture
def dossier_essoc2018(db, team_zam):
    from zam_repondeur.models import Dossier

    with transaction.manager:
        dossier = Dossier.create(
            uid="DLR5L15N36159",
            titre="Fonction publique : un Etat au service d'une société de confiance",
            slug="etat-service-societe-confiance",
        )
        dossier.team = team_zam

    return dossier


@pytest.fixture
def texte_essoc2018_an_premier_lecture_commission_fond(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            type_=TypeTexte.PROJET,
            chambre=Chambre.AN,
            legislature=15,
            numero=424,
            date_depot=date(2017, 11, 27),
        )

    return texte


@pytest.fixture
def lecture_essoc2018_an_premier_lecture_commission_fond(
    db, texte_essoc2018_an_premier_lecture_commission_fond, dossier_essoc2018
):
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
            texte=texte_essoc2018_an_premier_lecture_commission_fond,
            titre="Première lecture – Commission saisie au fond",
            organe="PO744107",
            dossier=dossier_essoc2018,
        )

    return lecture


@pytest.fixture
def texte_essoc2018_an_premiere_lecture_seance_publique(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            type_=TypeTexte.PROJET,
            chambre=Chambre.AN,
            legislature=15,
            numero=575,
            date_depot=date(2018, 1, 18),
        )

    return texte


@pytest.fixture
def lecture_essoc2018_an_premiere_lecture_seance_publique(
    db, texte_essoc2018_an_premiere_lecture_seance_publique, dossier_essoc2018
):
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
            texte=texte_essoc2018_an_premiere_lecture_seance_publique,
            titre="Première lecture – Séance publique",
            organe="PO717460",
            dossier=dossier_essoc2018,
        )

    return lecture


@pytest.fixture
def texte_essoc2018_senat_premiere_lecture_commission_fond(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            type_=TypeTexte.PROJET,
            chambre=Chambre.SENAT,
            session=2017,
            numero=259,
            date_depot=date(2018, 1, 31),
        )

    return texte


@pytest.fixture
def lecture_essoc2018_senat_premiere_lecture_commission_fond(
    db, texte_essoc2018_senat_premiere_lecture_commission_fond, dossier_essoc2018
):
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
            texte=texte_essoc2018_senat_premiere_lecture_commission_fond,
            titre="Première lecture – Commission saisie au fond",
            organe="PO748821",
            dossier=dossier_essoc2018,
        )

    return lecture


@pytest.fixture
def texte_essoc2018_senat_premiere_lecture_seance_publique(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            type_=TypeTexte.PROJET,
            chambre=Chambre.SENAT,
            session=2017,
            numero=330,
            date_depot=date(2018, 2, 22),
        )

    return texte


@pytest.fixture
def lecture_essoc2018_senat_premiere_lecture_seance_publique(
    db, texte_essoc2018_senat_premiere_lecture_seance_publique, dossier_essoc2018
):
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
            texte=texte_essoc2018_senat_premiere_lecture_seance_publique,
            titre="Première lecture – Séance publique",
            organe="PO78718",
            dossier=dossier_essoc2018,
        )

    return lecture


@pytest.fixture
def texte_essoc2018_an_nouvelle_lecture_commission_fond(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            type_=TypeTexte.PROJET,
            chambre=Chambre.AN,
            legislature=15,
            numero=806,
            date_depot=date(2018, 3, 21),
        )

    return texte


@pytest.fixture
def lecture_essoc2018_an_nouvelle_lecture_commission_fond(
    db, texte_essoc2018_an_nouvelle_lecture_commission_fond, dossier_essoc2018
):
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.NOUVELLE_LECTURE,
            texte=texte_essoc2018_an_nouvelle_lecture_commission_fond,
            titre="Nouvelle lecture – Commission saisie au fond",
            organe="PO744107",
            dossier=dossier_essoc2018,
        )

    return lecture


@pytest.fixture
def texte_essoc2018_an_nouvelle_lecture_seance_publique(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            type_=TypeTexte.PROJET,
            chambre=Chambre.AN,
            legislature=15,
            numero=1056,
            date_depot=date(2018, 6, 13),
        )

    return texte


@pytest.fixture
def lecture_essoc2018_an_nouvelle_lecture_seance_publique(
    db, texte_essoc2018_an_nouvelle_lecture_seance_publique, dossier_essoc2018
):
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.NOUVELLE_LECTURE,
            texte=texte_essoc2018_an_nouvelle_lecture_seance_publique,
            titre="Nouvelle lecture – Séance publique",
            organe="PO717460",
            dossier=dossier_essoc2018,
        )

    return lecture
