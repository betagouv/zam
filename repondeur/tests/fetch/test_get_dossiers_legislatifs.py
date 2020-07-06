import datetime
import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

HERE = Path(os.path.dirname(__file__))
DOSSIERS = HERE / "sample_data" / "Dossiers_Legislatifs_XV.json.zip"


@pytest.fixture(scope="module")
def dossiers_and_textes():
    from zam_repondeur.services.fetch.an.common import extract_from_zip
    from zam_repondeur.services.fetch.an.dossiers.dossiers_legislatifs import (
        get_dossiers_legislatifs_and_textes,
    )

    with patch(
        "zam_repondeur.services.fetch.an.dossiers.dossiers_legislatifs"
        ".extract_from_remote_zip"
    ) as extract:
        extract.return_value = extract_from_zip(open(DOSSIERS, "rb"))
        dossiers_by_uid, textes_by_uid = get_dossiers_legislatifs_and_textes(15)

    return dossiers_by_uid, textes_by_uid


@pytest.fixture(scope="module")
def dossiers(dossiers_and_textes):
    return dossiers_and_textes[0]


@pytest.fixture(scope="module")
def textes(dossiers_and_textes):
    return dossiers_and_textes[1]


def test_number_of_dossiers(dossiers):
    assert len(dossiers) == 1648


@pytest.fixture
def dossier_plfss_2018():
    with open(HERE / "sample_data" / "dossier-DLR5L15N36030.json") as f_:
        return json.load(f_)["dossierParlementaire"]


def test_parse_dossier_plfss_2018(dossier_plfss_2018, textes):
    from zam_repondeur.models.chambre import Chambre
    from zam_repondeur.models.phase import Phase
    from zam_repondeur.services.fetch.an.dossiers.dossiers_legislatifs import (
        parse_dossier,
    )
    from zam_repondeur.services.fetch.an.dossiers.models import (
        LectureRef,
        TexteRef,
        TypeTexte,
    )

    dossier = parse_dossier(dossier_plfss_2018, textes)

    assert dossier.uid == "DLR5L15N36030"
    assert dossier.titre == "Sécurité sociale : loi de financement 2018"
    texte_269 = TexteRef(
        uid="PRJLANR5L15B0269",
        type_=TypeTexte.PROJET,
        chambre=Chambre.AN,
        legislature=15,
        numero=269,
        titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
        titre_court="PLFSS pour 2018",
        date_depot=datetime.date(2017, 10, 11),
    )
    texte_63 = TexteRef(
        uid="PRJLSNR5S299B0063",
        type_=TypeTexte.PROJET,
        chambre=Chambre.SENAT,
        legislature=None,
        numero=63,
        titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
        titre_court="PLFSS pour 2018",
        date_depot=datetime.date(2017, 11, 6),
    )
    texte_387 = TexteRef(
        uid="PRJLANR5L15B0387",
        type_=TypeTexte.PROJET,
        chambre=Chambre.AN,
        legislature=15,
        numero=387,
        titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
        titre_court="PLFSS pour 2018",
        date_depot=datetime.date(2017, 11, 21),
    )
    texte_121 = TexteRef(
        uid="PRJLSNR5S299B0121",
        type_=TypeTexte.PROJET,
        chambre=Chambre.SENAT,
        legislature=None,
        numero=121,
        titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
        titre_court="PLFSS pour 2018",
        date_depot=datetime.date(2017, 11, 30),
    )
    texte_434 = TexteRef(
        uid="PRJLANR5L15B0434",
        type_=TypeTexte.PROJET,
        chambre=Chambre.AN,
        legislature=15,
        numero=434,
        titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
        titre_court="PLFSS pour 2018",
        date_depot=datetime.date(2017, 12, 1),
    )
    assert dossier.lectures == [
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie au fond",
            texte=texte_269,
            organe="PO420120",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=texte_269,
            organe="PO59048",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Séance publique",
            texte=texte_269,
            organe="PO717460",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.SENAT,
            titre="Première lecture – Commission saisie au fond",
            texte=texte_63,
            organe="PO211493",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.SENAT,
            titre="Première lecture – Commission saisie pour avis",
            texte=texte_63,
            organe="PO211494",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.SENAT,
            titre="Première lecture – Séance publique",
            texte=texte_63,
            organe="PO78718",
        ),
        LectureRef(
            phase=Phase.NOUVELLE_LECTURE,
            chambre=Chambre.AN,
            titre="Nouvelle lecture – Commission saisie au fond",
            texte=texte_387,
            organe="PO420120",
        ),
        LectureRef(
            phase=Phase.NOUVELLE_LECTURE,
            chambre=Chambre.AN,
            titre="Nouvelle lecture – Séance publique",
            texte=texte_387,
            organe="PO717460",
        ),
        LectureRef(
            phase=Phase.NOUVELLE_LECTURE,
            chambre=Chambre.SENAT,
            titre="Nouvelle lecture – Commission saisie au fond",
            texte=texte_121,
            organe="PO211493",
        ),
        LectureRef(
            phase=Phase.NOUVELLE_LECTURE,
            chambre=Chambre.SENAT,
            titre="Nouvelle lecture – Séance publique",
            texte=texte_121,
            organe="PO78718",
        ),
        LectureRef(
            phase=Phase.LECTURE_DEFINITIVE,
            chambre=Chambre.AN,
            titre="Lecture définitive – Commission saisie au fond",
            texte=texte_434,
            organe="PO420120",
        ),
        LectureRef(
            phase=Phase.LECTURE_DEFINITIVE,
            chambre=Chambre.AN,
            titre="Lecture définitive – Séance publique",
            texte=texte_434,
            organe="PO717460",
        ),
    ]


@pytest.fixture
def dossier_ecole_de_la_confiance():
    with open(HERE / "sample_data" / "dossier-DLR5L15N37055.json") as f_:
        return json.load(f_)["dossierParlementaire"]


def test_parse_dossier_ecole_de_la_confiance(dossier_ecole_de_la_confiance, textes):
    from zam_repondeur.models.chambre import Chambre
    from zam_repondeur.models.phase import Phase
    from zam_repondeur.services.fetch.an.dossiers.dossiers_legislatifs import (
        parse_dossier,
    )

    dossier = parse_dossier(dossier_ecole_de_la_confiance, textes)

    assert dossier.uid == "DLR5L15N37055"
    assert dossier.titre == "Ecole de la confiance"

    lecture = dossier.lectures[2]
    assert lecture.phase == Phase.PREMIERE_LECTURE
    assert lecture.chambre == Chambre.SENAT
    assert lecture.organe == "PO211490"  # commission
    assert lecture.texte.numero == 323
    assert lecture.partie is None

    lecture = dossier.lectures[3]
    assert lecture.phase == Phase.PREMIERE_LECTURE
    assert lecture.chambre == Chambre.SENAT
    assert lecture.organe == "PO78718"  # séance publique
    assert lecture.texte.numero == 474
    assert lecture.partie is None


@pytest.fixture
def dossier_plf_2018():
    with open(HERE / "sample_data" / "dossier-DLR5L15N35854.json") as f_:
        return json.load(f_)["dossierParlementaire"]


def test_parse_dossier_plf_2018(dossier_plf_2018, textes):
    from zam_repondeur.models.chambre import Chambre
    from zam_repondeur.models.phase import Phase
    from zam_repondeur.services.fetch.an.dossiers.dossiers_legislatifs import (
        parse_dossier,
    )
    from zam_repondeur.services.fetch.an.dossiers.models import (
        LectureRef,
        TexteRef,
        TypeTexte,
    )

    dossier = parse_dossier(dossier_plf_2018, textes)

    assert dossier.uid == "DLR5L15N35854"
    assert dossier.titre == "Budget : loi de finances 2018"
    texte_235 = TexteRef(
        uid="PRJLANR5L15B0235",
        type_=TypeTexte.PROJET,
        chambre=Chambre.AN,
        legislature=15,
        numero=235,
        titre_long="projet de loi de finances pour 2018",
        titre_court="PLF pour 2018",
        date_depot=datetime.date(2017, 9, 27),
    )
    texte_107 = TexteRef(
        uid="PRJLSNR5S299B0107",
        type_=TypeTexte.PROJET,
        chambre=Chambre.SENAT,
        legislature=None,
        numero=107,
        titre_long="projet de loi de finances pour 2018",
        titre_court="PLF pour 2018",
        date_depot=datetime.date(2017, 11, 23),
    )
    texte_485 = TexteRef(
        uid="PRJLANR5L15B0485",
        type_=TypeTexte.PROJET,
        chambre=Chambre.AN,
        legislature=15,
        numero=485,
        titre_long="projet de loi de finances pour 2018",
        titre_court="PLF pour 2018",
        date_depot=datetime.date(2017, 12, 12),
    )
    texte_172 = TexteRef(
        uid="PRJLSNR5S299B0172",
        type_=TypeTexte.PROJET,
        chambre=Chambre.SENAT,
        legislature=None,
        numero=172,
        titre_long="projet de loi de finances pour 2018",
        titre_court="PLF pour 2018",
        date_depot=datetime.date(2017, 12, 18),
    )
    texte_506 = TexteRef(
        uid="PRJLANR5L15B0506",
        type_=TypeTexte.PROJET,
        chambre=Chambre.AN,
        legislature=15,
        numero=506,
        titre_long="projet de loi de finances pour 2018",
        titre_court="PLF pour 2018",
        date_depot=datetime.date(2017, 12, 19),
    )
    assert dossier.lectures == [
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie au fond",
            texte=texte_235,
            partie=1,
            organe="PO59048",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie au fond",
            texte=texte_235,
            partie=2,
            organe="PO59048",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=texte_235,
            partie=1,
            organe="PO420120",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=texte_235,
            partie=2,
            organe="PO420120",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=texte_235,
            partie=1,
            organe="PO419604",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=texte_235,
            partie=2,
            organe="PO419604",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=texte_235,
            partie=1,
            organe="PO419610",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=texte_235,
            partie=2,
            organe="PO419610",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=texte_235,
            partie=1,
            organe="PO59047",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=texte_235,
            partie=2,
            organe="PO59047",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=texte_235,
            partie=1,
            organe="PO59046",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=texte_235,
            partie=2,
            organe="PO59046",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=texte_235,
            partie=1,
            organe="PO59051",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=texte_235,
            partie=2,
            organe="PO59051",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=texte_235,
            partie=1,
            organe="PO419865",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=texte_235,
            partie=2,
            organe="PO419865",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Séance publique",
            texte=texte_235,
            partie=1,
            organe="PO717460",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.AN,
            titre="Première lecture – Séance publique",
            texte=texte_235,
            partie=2,
            organe="PO717460",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.SENAT,
            titre="Première lecture – Commission saisie au fond",
            texte=texte_107,
            partie=1,
            organe="PO211494",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.SENAT,
            titre="Première lecture – Commission saisie au fond",
            texte=texte_107,
            partie=2,
            organe="PO211494",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.SENAT,
            titre="Première lecture – Séance publique",
            texte=texte_107,
            partie=1,
            organe="PO78718",
        ),
        LectureRef(
            phase=Phase.PREMIERE_LECTURE,
            chambre=Chambre.SENAT,
            titre="Première lecture – Séance publique",
            texte=texte_107,
            partie=2,
            organe="PO78718",
        ),
        LectureRef(
            phase=Phase.NOUVELLE_LECTURE,
            chambre=Chambre.AN,
            titre="Nouvelle lecture – Commission saisie au fond",
            texte=texte_485,
            organe="PO59048",
        ),
        LectureRef(
            phase=Phase.NOUVELLE_LECTURE,
            chambre=Chambre.AN,
            titre="Nouvelle lecture – Séance publique",
            texte=texte_485,
            organe="PO717460",
        ),
        LectureRef(
            phase=Phase.NOUVELLE_LECTURE,
            chambre=Chambre.SENAT,
            titre="Nouvelle lecture – Commission saisie au fond",
            texte=texte_172,
            organe="PO211494",
        ),
        LectureRef(
            phase=Phase.NOUVELLE_LECTURE,
            chambre=Chambre.SENAT,
            titre="Nouvelle lecture – Séance publique",
            texte=texte_172,
            organe="PO78718",
        ),
        LectureRef(
            phase=Phase.LECTURE_DEFINITIVE,
            chambre=Chambre.AN,
            titre="Lecture définitive – Commission saisie au fond",
            texte=texte_506,
            organe="PO59048",
        ),
        LectureRef(
            phase=Phase.LECTURE_DEFINITIVE,
            chambre=Chambre.AN,
            titre="Lecture définitive – Séance publique",
            texte=texte_506,
            organe="PO717460",
        ),
    ]


@pytest.fixture
def dossier_essoc():
    with open(HERE / "sample_data" / "dossier-DLR5L15N36159.json") as f_:
        return json.load(f_)["dossierParlementaire"]


def test_parse_dossier_essoc(dossier_essoc, textes):
    from zam_repondeur.models.chambre import Chambre
    from zam_repondeur.models.phase import Phase
    from zam_repondeur.services.fetch.an.dossiers.dossiers_legislatifs import (
        parse_dossier,
    )
    from zam_repondeur.services.fetch.an.dossiers.models import (
        DossierRef,
        LectureRef,
        TexteRef,
        TypeTexte,
    )

    lectures = [
        LectureRef(
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie au fond",
            phase=Phase.PREMIERE_LECTURE,
            texte=TexteRef(
                uid="PRJLANR5L15B0424",
                type_=TypeTexte.PROJET,
                chambre=Chambre.AN,
                legislature=15,
                numero=424,
                titre_long="projet de loi pour un Etat au service d’une société de confiance",  # noqa
                titre_court="Etat service société de confiance",
                date_depot=datetime.date(2017, 11, 27),
            ),
            organe="PO744107",
        ),
        LectureRef(
            chambre=Chambre.AN,
            titre="Première lecture – Séance publique",
            phase=Phase.PREMIERE_LECTURE,
            texte=TexteRef(
                uid="PRJLANR5L15BTC0575",
                type_=TypeTexte.PROJET,
                chambre=Chambre.AN,
                legislature=15,
                numero=575,
                titre_long="projet de loi sur le projet de loi, après engagement de la procédure accélérée, pour un Etat au service d’une société de confiance (n°424).",  # noqa
                titre_court="Etat service société de confiance",
                date_depot=datetime.date(2018, 1, 18),
            ),
            organe="PO717460",
        ),
        LectureRef(
            chambre=Chambre.SENAT,
            titre="Première lecture – Commission saisie au fond",
            phase=Phase.PREMIERE_LECTURE,
            texte=TexteRef(
                uid="PRJLSNR5S299B0259",
                type_=TypeTexte.PROJET,
                chambre=Chambre.SENAT,
                legislature=None,
                numero=259,
                titre_long="projet de loi pour un Etat au service d'une société de confiance",  # noqa
                titre_court="État au service d'une société de confiance",
                date_depot=datetime.date(2018, 1, 31),
            ),
            organe="PO748821",
        ),
        LectureRef(
            chambre=Chambre.SENAT,
            titre="Première lecture – Séance publique",
            phase=Phase.PREMIERE_LECTURE,
            texte=TexteRef(
                uid="PRJLSNR5S299BTC0330",
                type_=TypeTexte.PROJET,
                chambre=Chambre.SENAT,
                legislature=None,
                numero=330,
                titre_long="projet de loi  sur le projet de loi, adopté, par l'Assemblée nationale après engagement de la procédure accélérée, pour un Etat au service d'une société de confiance (n°259).",  # noqa
                titre_court="État au service d'une société de confiance",
                date_depot=datetime.date(2018, 2, 22),
            ),
            organe="PO78718",
        ),
        LectureRef(
            phase=Phase.NOUVELLE_LECTURE,
            chambre=Chambre.AN,
            titre="Nouvelle lecture – Commission saisie au fond",
            texte=TexteRef(
                uid="PRJLANR5L15B0806",
                type_=TypeTexte.PROJET,
                chambre=Chambre.AN,
                legislature=15,
                numero=806,
                titre_long="projet de loi renforçant l'efficacité de l'administration pour une relation de confiance avec le public",  # noqa
                titre_court="Renforcement de l'efficacité de l'administration pour une relation de confiance avec le public",  # noqa
                date_depot=datetime.date(2018, 3, 21),
            ),
            organe="PO744107",
        ),
        LectureRef(
            phase=Phase.NOUVELLE_LECTURE,
            chambre=Chambre.AN,
            titre="Nouvelle lecture – Séance publique",
            texte=TexteRef(
                uid="PRJLANR5L15BTC1056",
                type_=TypeTexte.PROJET,
                chambre=Chambre.AN,
                legislature=15,
                numero=1056,
                titre_long="projet de loi , en nouvelle lecture, sur le projet de loi, modifié par le Sénat, renforçant l'efficacité de l'administration pour une relation de confiance avec le public (n°806).",  # noqa
                titre_court="Etat au service d'une société de confiance",
                date_depot=datetime.date(2018, 6, 13),
            ),
            organe="PO717460",
        ),
    ]

    dossier = parse_dossier(dossier_essoc, textes)

    for lecture1, lecture2 in zip(dossier.lectures, lectures):
        assert lecture1 == lecture2

    assert dossier == DossierRef(
        uid="DLR5L15N36159",
        titre="Fonction publique : un Etat au service d'une société de confiance",
        slug="etat-service-societe-confiance",
        an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/etat_service_societe_confiance",  # noqa
        senat_url="http://www.senat.fr/dossier-legislatif/pjl17-259.html",
        lectures=lectures,
    )


@pytest.fixture
def dossier_pacte_ferroviaire():
    with open(HERE / "sample_data" / "dossier-DLR5L15N36460.json") as f_:
        return json.load(f_)["dossierParlementaire"]


def test_dossier_pacte_ferroviaire(dossier_pacte_ferroviaire, textes):
    from zam_repondeur.services.fetch.an.dossiers.dossiers_legislatifs import (
        parse_dossier,
    )

    dossier = parse_dossier(dossier_pacte_ferroviaire, textes)

    assert dossier.uid == "DLR5L15N36460"
    assert len(dossier.lectures) > 4


def test_extract_actes(dossier_essoc):
    from zam_repondeur.services.fetch.an.dossiers.dossiers_legislatifs import (
        extract_actes,
    )

    assert len(extract_actes(dossier_essoc)) == 4


class TestGenLectures:
    def test_gen_lectures_essoc(self, dossier_essoc, textes):
        from zam_repondeur.services.fetch.an.dossiers.dossiers_legislatifs import (
            gen_lectures,
        )

        acte = dossier_essoc["actesLegislatifs"]["acteLegislatif"][0]

        lectures = list(gen_lectures(acte, textes, "DLR5L15N36159"))

        assert len(lectures) == 2
        assert "Commission saisie au fond" in lectures[0].titre
        assert "Séance publique" in lectures[1].titre

    def test_gen_lectures_pacte_ferroviaire(self, dossier_pacte_ferroviaire, textes):
        from zam_repondeur.services.fetch.an.dossiers.dossiers_legislatifs import (
            gen_lectures,
        )

        acte = dossier_pacte_ferroviaire["actesLegislatifs"]["acteLegislatif"][0]

        lectures = list(gen_lectures(acte, textes, "DLR5L15N36159"))

        assert len(lectures) == 3
        assert "Commission saisie au fond" in lectures[0].titre
        assert "Commission saisie pour avis" in lectures[1].titre
        assert "Séance publique" in lectures[2].titre


def test_walk_actes(dossier_essoc, textes):
    from zam_repondeur.models.phase import Phase
    from zam_repondeur.services.fetch.an.dossiers.dossiers_legislatifs import (
        Chambre,
        WalkResult,
        walk_actes,
    )

    acte = dossier_essoc["actesLegislatifs"]["acteLegislatif"][0]
    assert list(walk_actes(acte, "DLR5L15N36159")) == [
        WalkResult(
            chambre=Chambre.AN,
            phase=Phase.PREMIERE_LECTURE,
            etape="COM-FOND",
            organe="PO744107",
            texte_examine="PRJLANR5L15B0424",
        ),
        WalkResult(
            chambre=Chambre.AN,
            phase=Phase.PREMIERE_LECTURE,
            etape="DEBATS",
            organe="PO717460",
            texte_examine="PRJLANR5L15BTC0575",
        ),
    ]
