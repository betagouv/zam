import datetime
import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest


HERE = Path(os.path.dirname(__file__))


DOSSIERS = HERE / "sample_data" / "Dossiers_Legislatifs_XV.json"


@pytest.fixture(scope="module")
def textes():
    from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import parse_textes

    with open(DOSSIERS) as f_:
        data = json.load(f_)
    return parse_textes(data["export"])


@pytest.fixture(scope="module")
def dossiers():
    from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import (
        get_dossiers_legislatifs
    )

    with patch(
        "zam_repondeur.fetch.an.dossiers.dossiers_legislatifs.extract_from_remote_zip"
    ) as m_open:
        m_open.return_value = DOSSIERS.open()
        dossiers_by_uid = get_dossiers_legislatifs(15)

    return dossiers_by_uid


def test_number_of_dossiers(dossiers):
    assert len(dossiers) == 839


@pytest.fixture
def dossier_plfss_2018():
    with open(HERE / "sample_data" / "dossier-DLR5L15N36030.json") as f_:
        return json.load(f_)["dossierParlementaire"]


def test_parse_dossier_plfss_2018(dossier_plfss_2018, textes):
    from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import parse_dossier
    from zam_repondeur.fetch.an.dossiers.models import (
        Chambre,
        Lecture,
        Texte,
        TypeTexte,
    )

    dossier = parse_dossier(dossier_plfss_2018, textes)

    assert dossier.uid == "DLR5L15N36030"
    assert dossier.titre == "Sécurité sociale : loi de financement 2018"
    assert dossier.lectures == [
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie au fond",
            texte=Texte(
                uid="PRJLANR5L15B0269",
                type_=TypeTexte.PROJET,
                numero=269,
                titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                titre_court="PLFSS pour 2018",
                date_depot=datetime.date(2017, 10, 11),
            ),
            organe="PO420120",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=Texte(
                uid="PRJLANR5L15B0269",
                type_=TypeTexte.PROJET,
                numero=269,
                titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                titre_court="PLFSS pour 2018",
                date_depot=datetime.date(2017, 10, 11),
            ),
            organe="PO59048",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Séance publique",
            texte=Texte(
                uid="PRJLANR5L15B0269",
                type_=TypeTexte.PROJET,
                numero=269,
                titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                titre_court="PLFSS pour 2018",
                date_depot=datetime.date(2017, 10, 11),
            ),
            organe="PO717460",
        ),
        Lecture(
            chambre=Chambre.SENAT,
            titre="Première lecture – Commission saisie au fond",
            texte=Texte(
                uid="PRJLSNR5S299B0063",
                type_=TypeTexte.PROJET,
                numero=63,
                titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                titre_court="PLFSS pour 2018",
                date_depot=datetime.date(2017, 11, 6),
            ),
            organe="PO211493",
        ),
        Lecture(
            chambre=Chambre.SENAT,
            titre="Première lecture – Commission saisie pour avis",
            texte=Texte(
                uid="PRJLSNR5S299B0063",
                type_=TypeTexte.PROJET,
                numero=63,
                titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                titre_court="PLFSS pour 2018",
                date_depot=datetime.date(2017, 11, 6),
            ),
            organe="PO211494",
        ),
        Lecture(
            chambre=Chambre.SENAT,
            titre="Première lecture – Séance publique",
            texte=Texte(
                uid="PRJLSNR5S299B0063",
                type_=TypeTexte.PROJET,
                numero=63,
                titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                titre_court="PLFSS pour 2018",
                date_depot=datetime.date(2017, 11, 6),
            ),
            organe="PO78718",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Nouvelle lecture – Commission saisie au fond",
            texte=Texte(
                uid="PRJLANR5L15B0387",
                type_=TypeTexte.PROJET,
                numero=387,
                titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                titre_court="PLFSS pour 2018",
                date_depot=datetime.date(2017, 11, 21),
            ),
            organe="PO420120",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Nouvelle lecture – Séance publique",
            texte=Texte(
                uid="PRJLANR5L15B0387",
                type_=TypeTexte.PROJET,
                numero=387,
                titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                titre_court="PLFSS pour 2018",
                date_depot=datetime.date(2017, 11, 21),
            ),
            organe="PO717460",
        ),
        Lecture(
            chambre=Chambre.SENAT,
            titre="Nouvelle lecture – Commission saisie au fond",
            texte=Texte(
                uid="PRJLSNR5S299B0121",
                type_=TypeTexte.PROJET,
                numero=121,
                titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                titre_court="PLFSS pour 2018",
                date_depot=datetime.date(2017, 11, 30),
            ),
            organe="PO211493",
        ),
        Lecture(
            chambre=Chambre.SENAT,
            titre="Nouvelle lecture – Séance publique",
            texte=Texte(
                uid="PRJLSNR5S299B0121",
                type_=TypeTexte.PROJET,
                numero=121,
                titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                titre_court="PLFSS pour 2018",
                date_depot=datetime.date(2017, 11, 30),
            ),
            organe="PO78718",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Lecture définitive – Commission saisie au fond",
            texte=Texte(
                uid="PRJLANR5L15B0434",
                type_=TypeTexte.PROJET,
                numero=434,
                titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                titre_court="PLFSS pour 2018",
                date_depot=datetime.date(2017, 12, 1),
            ),
            organe="PO420120",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Lecture définitive – Séance publique",
            texte=Texte(
                uid="PRJLANR5L15B0434",
                type_=TypeTexte.PROJET,
                numero=434,
                titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                titre_court="PLFSS pour 2018",
                date_depot=datetime.date(2017, 12, 1),
            ),
            organe="PO717460",
        ),
    ]


@pytest.fixture
def dossier_plf_2018():
    with open(HERE / "sample_data" / "dossier-DLR5L15N35854.json") as f_:
        return json.load(f_)["dossierParlementaire"]


def test_parse_dossier_plf_2018(dossier_plf_2018, textes):
    from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import parse_dossier
    from zam_repondeur.fetch.an.dossiers.models import (
        Chambre,
        Lecture,
        Texte,
        TypeTexte,
    )

    dossier = parse_dossier(dossier_plf_2018, textes)

    assert dossier.uid == "DLR5L15N35854"
    assert dossier.titre == "Budget : loi de finances 2018"
    assert dossier.lectures == [
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie au fond",
            texte=Texte(
                uid="PRJLANR5L15B0235",
                type_=TypeTexte.PROJET,
                numero=235,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 9, 27),
            ),
            partie=1,
            organe="PO59048",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie au fond",
            texte=Texte(
                uid="PRJLANR5L15B0235",
                type_=TypeTexte.PROJET,
                numero=235,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 9, 27),
            ),
            partie=2,
            organe="PO59048",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=Texte(
                uid="PRJLANR5L15B0235",
                type_=TypeTexte.PROJET,
                numero=235,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 9, 27),
            ),
            partie=1,
            organe="PO420120",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=Texte(
                uid="PRJLANR5L15B0235",
                type_=TypeTexte.PROJET,
                numero=235,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 9, 27),
            ),
            partie=2,
            organe="PO420120",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=Texte(
                uid="PRJLANR5L15B0235",
                type_=TypeTexte.PROJET,
                numero=235,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 9, 27),
            ),
            partie=1,
            organe="PO419604",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=Texte(
                uid="PRJLANR5L15B0235",
                type_=TypeTexte.PROJET,
                numero=235,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 9, 27),
            ),
            partie=2,
            organe="PO419604",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=Texte(
                uid="PRJLANR5L15B0235",
                type_=TypeTexte.PROJET,
                numero=235,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 9, 27),
            ),
            partie=1,
            organe="PO419610",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=Texte(
                uid="PRJLANR5L15B0235",
                type_=TypeTexte.PROJET,
                numero=235,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 9, 27),
            ),
            partie=2,
            organe="PO419610",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=Texte(
                uid="PRJLANR5L15B0235",
                type_=TypeTexte.PROJET,
                numero=235,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 9, 27),
            ),
            partie=1,
            organe="PO59047",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=Texte(
                uid="PRJLANR5L15B0235",
                type_=TypeTexte.PROJET,
                numero=235,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 9, 27),
            ),
            partie=2,
            organe="PO59047",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=Texte(
                uid="PRJLANR5L15B0235",
                type_=TypeTexte.PROJET,
                numero=235,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 9, 27),
            ),
            partie=1,
            organe="PO59046",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=Texte(
                uid="PRJLANR5L15B0235",
                type_=TypeTexte.PROJET,
                numero=235,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 9, 27),
            ),
            partie=2,
            organe="PO59046",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=Texte(
                uid="PRJLANR5L15B0235",
                type_=TypeTexte.PROJET,
                numero=235,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 9, 27),
            ),
            partie=1,
            organe="PO59051",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=Texte(
                uid="PRJLANR5L15B0235",
                type_=TypeTexte.PROJET,
                numero=235,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 9, 27),
            ),
            partie=2,
            organe="PO59051",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=Texte(
                uid="PRJLANR5L15B0235",
                type_=TypeTexte.PROJET,
                numero=235,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 9, 27),
            ),
            partie=1,
            organe="PO419865",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Commission saisie pour avis",
            texte=Texte(
                uid="PRJLANR5L15B0235",
                type_=TypeTexte.PROJET,
                numero=235,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 9, 27),
            ),
            partie=2,
            organe="PO419865",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Séance publique",
            texte=Texte(
                uid="PRJLANR5L15B0235",
                type_=TypeTexte.PROJET,
                numero=235,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 9, 27),
            ),
            partie=1,
            organe="PO717460",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Première lecture – Séance publique",
            texte=Texte(
                uid="PRJLANR5L15B0235",
                type_=TypeTexte.PROJET,
                numero=235,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 9, 27),
            ),
            partie=2,
            organe="PO717460",
        ),
        Lecture(
            chambre=Chambre.SENAT,
            titre="Première lecture – Commission saisie au fond",
            texte=Texte(
                uid="PRJLSNR5S299B0107",
                type_=TypeTexte.PROJET,
                numero=107,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 11, 23),
            ),
            partie=1,
            organe="PO211494",
        ),
        Lecture(
            chambre=Chambre.SENAT,
            titre="Première lecture – Commission saisie au fond",
            texte=Texte(
                uid="PRJLSNR5S299B0107",
                type_=TypeTexte.PROJET,
                numero=107,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 11, 23),
            ),
            partie=2,
            organe="PO211494",
        ),
        Lecture(
            chambre=Chambre.SENAT,
            titre="Première lecture – Séance publique",
            texte=Texte(
                uid="PRJLSNR5S299B0107",
                type_=TypeTexte.PROJET,
                numero=107,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 11, 23),
            ),
            partie=1,
            organe="PO78718",
        ),
        Lecture(
            chambre=Chambre.SENAT,
            titre="Première lecture – Séance publique",
            texte=Texte(
                uid="PRJLSNR5S299B0107",
                type_=TypeTexte.PROJET,
                numero=107,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 11, 23),
            ),
            partie=2,
            organe="PO78718",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Nouvelle lecture – Commission saisie au fond",
            texte=Texte(
                uid="PRJLANR5L15B0485",
                type_=TypeTexte.PROJET,
                numero=485,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 12, 12),
            ),
            organe="PO59048",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Nouvelle lecture – Séance publique",
            texte=Texte(
                uid="PRJLANR5L15B0485",
                type_=TypeTexte.PROJET,
                numero=485,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 12, 12),
            ),
            organe="PO717460",
        ),
        Lecture(
            chambre=Chambre.SENAT,
            titre="Nouvelle lecture – Commission saisie au fond",
            texte=Texte(
                uid="PRJLSNR5S299B0172",
                type_=TypeTexte.PROJET,
                numero=172,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 12, 18),
            ),
            organe="PO211494",
        ),
        Lecture(
            chambre=Chambre.SENAT,
            titre="Nouvelle lecture – Séance publique",
            texte=Texte(
                uid="PRJLSNR5S299B0172",
                type_=TypeTexte.PROJET,
                numero=172,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 12, 18),
            ),
            organe="PO78718",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Lecture définitive – Commission saisie au fond",
            texte=Texte(
                uid="PRJLANR5L15B0506",
                type_=TypeTexte.PROJET,
                numero=506,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 12, 19),
            ),
            organe="PO59048",
        ),
        Lecture(
            chambre=Chambre.AN,
            titre="Lecture définitive – Séance publique",
            texte=Texte(
                uid="PRJLANR5L15B0506",
                type_=TypeTexte.PROJET,
                numero=506,
                titre_long="projet de loi de finances pour 2018",
                titre_court="PLF pour 2018",
                date_depot=datetime.date(2017, 12, 19),
            ),
            organe="PO717460",
        ),
    ]


@pytest.fixture
def dossier_essoc():
    with open(HERE / "sample_data" / "dossier-DLR5L15N36159.json") as f_:
        return json.load(f_)["dossierParlementaire"]


def test_parse_dossier_essoc(dossier_essoc, textes):
    from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import parse_dossier
    from zam_repondeur.fetch.an.dossiers.models import (
        Chambre,
        Lecture,
        Dossier,
        Texte,
        TypeTexte,
    )

    dossier = parse_dossier(dossier_essoc, textes)

    assert dossier == Dossier(
        uid="DLR5L15N36159",
        titre="Fonction publique : un Etat au service d'une société de confiance",
        lectures=[
            Lecture(
                chambre=Chambre.AN,
                titre="Première lecture – Commission saisie au fond",
                texte=Texte(
                    uid="PRJLANR5L15B0424",
                    type_=TypeTexte.PROJET,
                    numero=424,
                    titre_long="projet de loi pour un Etat au service d’une société de confiance",  # noqa
                    titre_court="Etat service société de confiance",
                    date_depot=datetime.date(2017, 11, 27),
                ),
                organe="PO744107",
            ),
            Lecture(
                chambre=Chambre.AN,
                titre="Première lecture – Séance publique",
                texte=Texte(
                    uid="PRJLANR5L15BTC0575",
                    type_=TypeTexte.PROJET,
                    numero=575,
                    titre_long="projet de loi sur le projet de loi, après engagement de la procédure accélérée, pour un Etat au service d’une société de confiance (n°424).",  # noqa
                    titre_court="Etat service société de confiance",
                    date_depot=datetime.date(2018, 1, 18),
                ),
                organe="PO717460",
            ),
            Lecture(
                chambre=Chambre.SENAT,
                titre="Première lecture – Commission saisie au fond",
                texte=Texte(
                    uid="PRJLSNR5S299B0259",
                    type_=TypeTexte.PROJET,
                    numero=259,
                    titre_long="projet de loi pour un Etat au service d'une société de confiance",  # noqa
                    titre_court="État au service d'une société de confiance",
                    date_depot=datetime.date(2018, 1, 31),
                ),
                organe="PO748821",
            ),
            Lecture(
                chambre=Chambre.SENAT,
                titre="Première lecture – Séance publique",
                texte=Texte(
                    uid="PRJLSNR5S299BTC0330",
                    type_=TypeTexte.PROJET,
                    numero=330,
                    titre_long="projet de loi  sur le projet de loi, adopté, par l'Assemblée nationale après engagement de la procédure accélérée, pour un Etat au service d'une société de confiance (n°259).",  # noqa
                    titre_court="État au service d'une société de confiance",
                    date_depot=datetime.date(2018, 2, 22),
                ),
                organe="PO78718",
            ),
            Lecture(
                chambre=Chambre.AN,
                titre="Nouvelle lecture – Commission saisie au fond",
                texte=Texte(
                    uid="PRJLANR5L15B0806",
                    type_=TypeTexte.PROJET,
                    numero=806,
                    titre_long="projet de loi renforçant l'efficacité de l'administration pour une relation de confiance avec le public",  # noqa
                    titre_court="Renforcement de l'efficacité de l'administration pour une relation de confiance avec le public",  # noqa
                    date_depot=datetime.date(2018, 3, 21),
                ),
                organe="PO744107",
            ),
            Lecture(
                chambre=Chambre.AN,
                titre="Nouvelle lecture – Séance publique",
                texte=Texte(
                    uid="PRJLANR5L15BTC1056",
                    type_=TypeTexte.PROJET,
                    numero=1056,
                    titre_long="projet de loi , en nouvelle lecture, sur le projet de loi, modifié par le Sénat, renforçant l'efficacité de l'administration pour une relation de confiance avec le public (n°806).",  # noqa
                    titre_court="Renforcement de l'efficacité de l'administration pour une relation de confiance avec le public",  # noqa
                    date_depot=datetime.date(2018, 6, 13),
                ),
                organe="PO717460",
            ),
        ],
    )


@pytest.fixture
def dossier_pacte_ferroviaire():
    with open(HERE / "sample_data" / "dossier-DLR5L15N36460.json") as f_:
        return json.load(f_)["dossierParlementaire"]


def test_dossier_pacte_ferroviaire(dossier_pacte_ferroviaire, textes):
    from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import parse_dossier

    dossier = parse_dossier(dossier_pacte_ferroviaire, textes)

    assert dossier.uid == "DLR5L15N36460"
    assert len(dossier.lectures) > 4


def test_extract_actes(dossier_essoc):
    from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import extract_actes

    assert len(extract_actes(dossier_essoc)) == 4


class TestGenLectures:
    def test_gen_lectures_essoc(self, dossier_essoc, textes):
        from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import gen_lectures

        acte = dossier_essoc["actesLegislatifs"]["acteLegislatif"][0]

        lectures = list(gen_lectures(acte, textes))

        assert len(lectures) == 2
        assert "Commission saisie au fond" in lectures[0].titre
        assert "Séance publique" in lectures[1].titre

    def test_gen_lectures_pacte_ferroviaire(self, dossier_pacte_ferroviaire, textes):
        from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import gen_lectures

        acte = dossier_pacte_ferroviaire["actesLegislatifs"]["acteLegislatif"][0]

        lectures = list(gen_lectures(acte, textes))

        assert len(lectures) == 3
        assert "Commission saisie au fond" in lectures[0].titre
        assert "Commission saisie pour avis" in lectures[1].titre
        assert "Séance publique" in lectures[2].titre


def test_walk_actes(dossier_essoc, textes):
    from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import (
        walk_actes,
        WalkResult,
    )

    acte = dossier_essoc["actesLegislatifs"]["acteLegislatif"][0]
    assert list(walk_actes(acte)) == [
        WalkResult(
            phase="COM-FOND",
            organe="PO744107",
            texte="PRJLANR5L15B0424",
            premiere_lecture=True,
        ),
        WalkResult(
            phase="DEBATS",
            organe="PO717460",
            texte="PRJLANR5L15BTC0575",
            premiere_lecture=True,
        ),
    ]
