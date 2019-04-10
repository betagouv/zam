from datetime import date

import pytest
import transaction


@pytest.fixture
def dossier_plf2018(db):
    from zam_repondeur.models import Dossier

    with transaction.manager:
        dossier = Dossier.create(
            uid="DLR5L15N35854", titre="Budget : loi de finances 2018"
        )

    return dossier


@pytest.fixture
def texte_plf2018_an_premiere_lecture(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            uid="PRJLANR5L15B0235",
            type_=TypeTexte.PROJET,
            chambre=Chambre.AN,
            legislature=15,
            numero=235,
            titre_long="projet de loi de finances pour 2018",
            titre_court="PLF pour 2018",
            date_depot=date(2017, 9, 27),
        )

    return texte


@pytest.fixture
def lecture_plf2018_an_premiere_lecture_commission_fond_1(
    db, dossier_plf2018, texte_plf2018_an_premiere_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            partie=1,
            texte=texte_plf2018_an_premiere_lecture,
            titre="Première lecture – Commission saisie au fond",
            organe="PO59048",
            dossier=dossier_plf2018,
        )

    return lecture


@pytest.fixture
def lecture_plf2018_an_premiere_lecture_commission_fond_2(
    db, dossier_plf2018, texte_plf2018_an_premiere_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            partie=2,
            texte=texte_plf2018_an_premiere_lecture,
            titre="Première lecture – Commission saisie au fond",
            organe="PO59048",
            dossier=dossier_plf2018,
        )

    return lecture


@pytest.fixture
def lecture_plf2018_an_premiere_lecture_commission_avis_1(
    db, dossier_plf2018, texte_plf2018_an_premiere_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            partie=1,
            texte=texte_plf2018_an_premiere_lecture,
            titre="Première lecture – Commission saisie pour avis",
            organe="PO420120",
            dossier=dossier_plf2018,
        )

    return lecture


@pytest.fixture
def lecture_plf2018_an_premiere_lecture_commission_avis_2(
    db, dossier_plf2018, texte_plf2018_an_premiere_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            partie=2,
            texte=texte_plf2018_an_premiere_lecture,
            titre="Première lecture – Commission saisie pour avis",
            organe="PO420120",
            dossier=dossier_plf2018,
        )

    return lecture


# 6 (x 2 parties) `Commission saisie pour avis` are
# NOT registered here for the sake of brevity.


@pytest.fixture
def lecture_plf2018_an_premiere_lecture_seance_publique_1(
    db, dossier_plf2018, texte_plf2018_an_premiere_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            partie=1,
            texte=texte_plf2018_an_premiere_lecture,
            titre="Première lecture – Séance publique",
            organe="PO717460",
            dossier=dossier_plf2018,
        )

    return lecture


@pytest.fixture
def lecture_plf2018_an_premiere_lecture_seance_publique_2(
    db, dossier_plf2018, texte_plf2018_an_premiere_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            partie=2,
            texte=texte_plf2018_an_premiere_lecture,
            titre="Première lecture – Séance publique",
            organe="PO717460",
            dossier=dossier_plf2018,
        )

    return lecture


@pytest.fixture
def texte_plf2018_senat_premiere_lecture(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            uid="PRJLSNR5S299B0107",
            type_=TypeTexte.PROJET,
            chambre=Chambre.SENAT,
            session=2017,
            numero=107,
            titre_long="projet de loi de finances pour 2018",
            titre_court="PLF pour 2018",
            date_depot=date(2017, 11, 23),
        )

    return texte


@pytest.fixture
def lecture_plf2018_senat_premiere_lecture_commission_fond_1(
    db, dossier_plf2018, texte_plf2018_senat_premiere_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="senat",
            session="2017-2018",
            partie=1,
            texte=texte_plf2018_senat_premiere_lecture,
            titre="Première lecture – Commission saisie au fond",
            organe="PO211494",
            dossier=dossier_plf2018,
        )

    return lecture


@pytest.fixture
def lecture_plf2018_senat_premiere_lecture_commission_fond_2(
    db, dossier_plf2018, texte_plf2018_senat_premiere_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="senat",
            session="2017-2018",
            partie=2,
            texte=texte_plf2018_senat_premiere_lecture,
            titre="Première lecture – Commission saisie au fond",
            organe="PO211494",
            dossier=dossier_plf2018,
        )

    return lecture


@pytest.fixture
def lecture_plf2018_senat_premiere_lecture_seance_publique_1(
    db, dossier_plf2018, texte_plf2018_senat_premiere_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="senat",
            session="2017-2018",
            partie=1,
            texte=texte_plf2018_senat_premiere_lecture,
            titre="Première lecture – Séance publique",
            organe="PO78718",
            dossier=dossier_plf2018,
        )

    return lecture


@pytest.fixture
def lecture_plf2018_senat_premiere_lecture_seance_publique_2(
    db, dossier_plf2018, texte_plf2018_senat_premiere_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="senat",
            session="2017-2018",
            partie=2,
            texte=texte_plf2018_senat_premiere_lecture,
            titre="Première lecture – Séance publique",
            organe="PO78718",
            dossier=dossier_plf2018,
        )

    return lecture


@pytest.fixture
def texte_plf2018_an_nouvelle_lecture(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            uid="PRJLANR5L15B0485",
            type_=TypeTexte.PROJET,
            chambre=Chambre.AN,
            legislature=15,
            numero=485,
            titre_long="projet de loi de finances pour 2018",
            titre_court="PLF pour 2018",
            date_depot=date(2017, 12, 12),
        )

    return texte


@pytest.fixture
def lecture_plf2018_an_nouvelle_lecture_commission_fond(
    db, dossier_plf2018, texte_plf2018_an_nouvelle_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            texte=texte_plf2018_an_nouvelle_lecture,
            titre="Nouvelle lecture – Commission saisie au fond",
            organe="PO59048",
            dossier=dossier_plf2018,
        )

    return lecture


@pytest.fixture
def lecture_plf2018_an_nouvelle_lecture_seance_publique(
    db, dossier_plf2018, texte_plf2018_an_nouvelle_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            texte=texte_plf2018_an_nouvelle_lecture,
            titre="Nouvelle lecture – Séance publique",
            organe="PO717460",
            dossier=dossier_plf2018,
        )

    return lecture


@pytest.fixture
def texte_plf2018_senat_nouvelle_lecture(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            uid="PRJLSNR5S299B0172",
            type_=TypeTexte.PROJET,
            chambre=Chambre.SENAT,
            session=2017,
            numero=172,
            titre_long="projet de loi de finances pour 2018",
            titre_court="PLF pour 2018",
            date_depot=date(2017, 12, 18),
        )

    return texte


@pytest.fixture
def lecture_plf2018_senat_nouvelle_lecture_commission_fond(
    db, dossier_plf2018, texte_plf2018_senat_nouvelle_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="senat",
            session="2017-2018",
            texte=texte_plf2018_senat_nouvelle_lecture,
            titre="Nouvelle lecture – Commission saisie au fond",
            organe="PO211494",
            dossier=dossier_plf2018,
        )

    return lecture


@pytest.fixture
def lecture_plf2018_senat_nouvelle_lecture_seance_publique(
    db, dossier_plf2018, texte_plf2018_senat_nouvelle_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="senat",
            session="2017-2018",
            texte=texte_plf2018_senat_nouvelle_lecture,
            titre="Nouvelle lecture – Séance publique",
            organe="PO78718",
            dossier=dossier_plf2018,
        )

    return lecture


@pytest.fixture
def texte_plf2018_an_lecture_definitive(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            uid="PRJLANR5L15B0506",
            type_=TypeTexte.PROJET,
            chambre=Chambre.AN,
            legislature=15,
            numero=506,
            titre_long="projet de loi de finances pour 2018",
            titre_court="PLF pour 2018",
            date_depot=date(2017, 12, 19),
        )

    return texte


@pytest.fixture
def lecture_plf2018_an_lecture_definitive_commission_fond(
    db, dossier_plf2018, texte_plf2018_an_lecture_definitive
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            texte=texte_plf2018_an_lecture_definitive,
            titre="Lecture définitive – Commission saisie au fond",
            organe="PO59048",
            dossier=dossier_plf2018,
        )

    return lecture


@pytest.fixture
def lecture_plf2018_an_lecture_definitive_seance_publique(
    db, dossier_plf2018, texte_plf2018_an_lecture_definitive
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            texte=texte_plf2018_an_lecture_definitive,
            titre="Lecture définitive – Séance publique",
            organe="PO717460",
            dossier=dossier_plf2018,
        )

    return lecture
