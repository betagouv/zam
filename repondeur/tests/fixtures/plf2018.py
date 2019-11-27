from datetime import date

import pytest
import transaction


@pytest.fixture
def dossier_plf2018(db, team_zam):
    from zam_repondeur.models import Dossier

    with transaction.manager:
        dossier = Dossier.create(
            an_id="DLR5L15N35854",
            titre="Budget : loi de finances 2018",
            slug="loi-finances-2018",
        )
        dossier.team = team_zam

    return dossier


@pytest.fixture
def texte_plf2018_an_premiere_lecture(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            type_=TypeTexte.PROJET,
            chambre=Chambre.AN,
            legislature=15,
            numero=235,
            date_depot=date(2017, 9, 27),
        )

    return texte


@pytest.fixture
def lecture_plf2018_an_premiere_lecture_commission_fond_1(
    db, dossier_plf2018, texte_plf2018_an_premiere_lecture
):
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
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
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
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
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
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
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
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
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
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
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
            partie=2,
            texte=texte_plf2018_an_premiere_lecture,
            titre="Première lecture – Séance publique",
            organe="PO717460",
            dossier=dossier_plf2018,
        )

    return lecture


@pytest.fixture
def article1_plf2018_an_premiere_lecture_seance_publique_2(
    db, lecture_plf2018_an_premiere_lecture_seance_publique_2
):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(
            lecture=lecture_plf2018_an_premiere_lecture_seance_publique_2,
            type="article",
            num="1",
        )

    return article


@pytest.fixture
def amendements_plf2018_an_premiere_lecture_seance_publique_2(
    db,
    lecture_plf2018_an_premiere_lecture_seance_publique_2,
    article1_plf2018_an_premiere_lecture_seance_publique_2,
):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        amendements = [
            Amendement.create(
                lecture=lecture_plf2018_an_premiere_lecture_seance_publique_2,
                article=article1_plf2018_an_premiere_lecture_seance_publique_2,
                num=num,
                position=position,
                mission_titre="Mission Action et transformation publiques",
                mission_titre_court="Action transfo.",
            )
            for position, num in enumerate((111, 333), 1)
        ]

    DBSession.add_all(amendements)
    return amendements


@pytest.fixture
def texte_plf2018_senat_premiere_lecture(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            type_=TypeTexte.PROJET,
            chambre=Chambre.SENAT,
            session=2017,
            numero=107,
            date_depot=date(2017, 11, 23),
        )

    return texte


@pytest.fixture
def lecture_plf2018_senat_premiere_lecture_commission_fond_1(
    db, dossier_plf2018, texte_plf2018_senat_premiere_lecture
):
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
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
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
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
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
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
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
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
            type_=TypeTexte.PROJET,
            chambre=Chambre.AN,
            legislature=15,
            numero=485,
            date_depot=date(2017, 12, 12),
        )

    return texte


@pytest.fixture
def lecture_plf2018_an_nouvelle_lecture_commission_fond(
    db, dossier_plf2018, texte_plf2018_an_nouvelle_lecture
):
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.NOUVELLE_LECTURE,
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
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.NOUVELLE_LECTURE,
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
            type_=TypeTexte.PROJET,
            chambre=Chambre.SENAT,
            session=2017,
            numero=172,
            date_depot=date(2017, 12, 18),
        )

    return texte


@pytest.fixture
def lecture_plf2018_senat_nouvelle_lecture_commission_fond(
    db, dossier_plf2018, texte_plf2018_senat_nouvelle_lecture
):
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.NOUVELLE_LECTURE,
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
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.NOUVELLE_LECTURE,
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
            type_=TypeTexte.PROJET,
            chambre=Chambre.AN,
            legislature=15,
            numero=506,
            date_depot=date(2017, 12, 19),
        )

    return texte


@pytest.fixture
def lecture_plf2018_an_lecture_definitive_commission_fond(
    db, dossier_plf2018, texte_plf2018_an_lecture_definitive
):
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.NOUVELLE_LECTURE,
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
    from zam_repondeur.models import Lecture, Phase

    with transaction.manager:
        lecture = Lecture.create(
            phase=Phase.NOUVELLE_LECTURE,
            texte=texte_plf2018_an_lecture_definitive,
            titre="Lecture définitive – Séance publique",
            organe="PO717460",
            dossier=dossier_plf2018,
        )

    return lecture
