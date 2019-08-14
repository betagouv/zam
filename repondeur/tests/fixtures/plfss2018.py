from datetime import date

import pytest
import transaction


@pytest.fixture
def dossier_plfss2018(db, team_zam):
    from zam_repondeur.models import Dossier

    with transaction.manager:
        dossier = Dossier.create(
            uid="DLR5L15N36030",
            titre="Sécurité sociale : loi de financement 2018",
            slug="plfss-2018",
        )
        dossier.team = team_zam

    return dossier


@pytest.fixture
def texte_plfss2018_an_premiere_lecture(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            type_=TypeTexte.PROJET,
            chambre=Chambre.AN,
            legislature=15,
            numero=269,
            date_depot=date(2017, 10, 11),
        )

    return texte


@pytest.fixture
def lecture_plfss2018_an_premiere_lecture_commission_fond(
    db, dossier_plfss2018, texte_plfss2018_an_premiere_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            texte=texte_plfss2018_an_premiere_lecture,
            titre="Première lecture – Commission saisie au fond",
            organe="PO420120",
            dossier=dossier_plfss2018,
        )

    return lecture


@pytest.fixture
def lecture_plfss2018_an_premiere_lecture_commission_avis(
    db, dossier_plfss2018, texte_plfss2018_an_premiere_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            texte=texte_plfss2018_an_premiere_lecture,
            titre="Première lecture – Commission saisie pour avis",
            organe="PO59048",
            dossier=dossier_plfss2018,
        )

    return lecture


@pytest.fixture
def lecture_plfss2018_an_premiere_lecture_seance_publique(
    db, dossier_plfss2018, texte_plfss2018_an_premiere_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            texte=texte_plfss2018_an_premiere_lecture,
            titre="Première lecture – Séance publique",
            organe="PO717460",
            dossier=dossier_plfss2018,
        )

    return lecture


@pytest.fixture
def texte_plfss2018_senat_premiere_lecture(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            type_=TypeTexte.PROJET,
            chambre=Chambre.SENAT,
            session=2017,
            numero=63,
            date_depot=date(2017, 11, 6),
        )

    return texte


@pytest.fixture
def lecture_plfss2018_senat_premiere_lecture_commission_fond(
    db, dossier_plfss2018, texte_plfss2018_senat_premiere_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            texte=texte_plfss2018_senat_premiere_lecture,
            titre="Première lecture – Commission saisie au fond",
            organe="PO211493",
            dossier=dossier_plfss2018,
        )

    return lecture


@pytest.fixture
def lecture_plfss2018_senat_premiere_lecture_commission_avis(
    db, dossier_plfss2018, texte_plfss2018_senat_premiere_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            texte=texte_plfss2018_senat_premiere_lecture,
            titre="Première lecture – Commission saisie pour avis",
            organe="PO211494",
            dossier=dossier_plfss2018,
        )

    return lecture


@pytest.fixture
def lecture_plfss2018_senat_premiere_lecture_seance_publique(
    db, dossier_plfss2018, texte_plfss2018_senat_premiere_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            texte=texte_plfss2018_senat_premiere_lecture,
            titre="Première lecture – Séance publique",
            organe="PO78718",
            dossier=dossier_plfss2018,
        )

    return lecture


@pytest.fixture
def texte_plfss2018_an_nouvelle_lecture(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            type_=TypeTexte.PROJET,
            chambre=Chambre.AN,
            legislature=15,
            numero=387,
            date_depot=date(2017, 11, 21),
        )

    return texte


@pytest.fixture
def lecture_plfss2018_an_nouvelle_lecture_commission_fond(
    db, dossier_plfss2018, texte_plfss2018_an_nouvelle_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            texte=texte_plfss2018_an_nouvelle_lecture,
            titre="Nouvelle lecture – Commission saisie au fond",
            organe="PO420120",
            dossier=dossier_plfss2018,
        )

    return lecture


@pytest.fixture
def lecture_plfss2018_an_nouvelle_lecture_seance_publique(
    db, dossier_plfss2018, texte_plfss2018_an_nouvelle_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            texte=texte_plfss2018_an_nouvelle_lecture,
            titre="Nouvelle lecture – Séance publique",
            organe="PO717460",
            dossier=dossier_plfss2018,
        )

    return lecture


@pytest.fixture
def texte_plfss2018_senat_nouvelle_lecture(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            type_=TypeTexte.PROJET,
            chambre=Chambre.SENAT,
            session=2017,
            numero=121,
            date_depot=date(2017, 11, 30),
        )

    return texte


@pytest.fixture
def lecture_plfss2018_senat_nouvelle_lecture_commission_fond(
    db, dossier_plfss2018, texte_plfss2018_senat_nouvelle_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            texte=texte_plfss2018_senat_nouvelle_lecture,
            titre="Nouvelle lecture – Commission saisie au fond",
            organe="PO211493",
            dossier=dossier_plfss2018,
        )

    return lecture


@pytest.fixture
def lecture_plfss2018_senat_nouvelle_lecture_seance_publique(
    db, dossier_plfss2018, texte_plfss2018_senat_nouvelle_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            texte=texte_plfss2018_senat_nouvelle_lecture,
            titre="Nouvelle lecture – Séance publique",
            organe="PO78718",
            dossier=dossier_plfss2018,
        )

    return lecture


@pytest.fixture
def texte_plfss2018_an_lecture_definitive(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            type_=TypeTexte.PROJET,
            chambre=Chambre.AN,
            legislature=15,
            numero=434,
            date_depot=date(2017, 12, 1),
        )

    return texte


@pytest.fixture
def lecture_plfss2018_an_lecture_definitive_commission_fond(
    db, dossier_plfss2018, texte_plfss2018_an_lecture_definitive
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            texte=texte_plfss2018_an_lecture_definitive,
            titre="Lecture définitive – Commission saisie au fond",
            organe="PO420120",
            dossier=dossier_plfss2018,
        )

    return lecture


@pytest.fixture
def lecture_plfss2018_an_lecture_definitive_seance_publique(
    db, dossier_plfss2018, texte_plfss2018_an_lecture_definitive
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            texte=texte_plfss2018_an_lecture_definitive,
            titre="Lecture définitive – Séance publique",
            organe="PO717460",
            dossier=dossier_plfss2018,
        )

    return lecture
