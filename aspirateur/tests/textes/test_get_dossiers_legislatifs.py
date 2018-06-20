import os
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest


HERE = Path(os.path.dirname(__file__))


@pytest.fixture
def sample_file():
    path = HERE.parent / "sample_data" / "Dossiers_Legislatifs_XV.json"
    return path.open()


def test_an_get_dossiers_legislatifs(sample_file):
    from zam_aspirateur.textes.dossiers_legislatifs import get_dossiers_legislatifs
    from zam_aspirateur.textes.models import Chambre, Lecture, Dossier, Texte, TypeTexte

    with patch(
        "zam_aspirateur.textes.dossiers_legislatifs.extract_from_remote_zip"
    ) as m_open:
        m_open.return_value = sample_file
        dossiers_by_uid = get_dossiers_legislatifs(legislature=15)

    dossiers = list(dossiers_by_uid.values())
    assert len(dossiers) == 605
    assert dossiers[324] == Dossier(
        uid="DLR5L15N36030",
        titre="Sécurité sociale : loi de financement 2018",
        lectures={
            "PRJLANR5L15B0269": Lecture(
                chambre=Chambre.AN,
                titre="Première lecture",
                texte=Texte(
                    uid="PRJLANR5L15B0269",
                    type_=TypeTexte.PROJET,
                    numero=269,
                    titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                    titre_court="PLFSS pour 2018",
                    date_depot=date(2017, 10, 11),
                ),
            ),
            "PRJLSNR5S299B0063": Lecture(
                chambre=Chambre.SENAT,
                titre="Première lecture",
                texte=Texte(
                    uid="PRJLSNR5S299B0063",
                    type_=TypeTexte.PROJET,
                    numero=63,
                    titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                    titre_court="PLFSS pour 2018",
                    date_depot=date(2017, 11, 6),
                ),
            ),
            "PRJLANR5L15B0387": Lecture(
                chambre=Chambre.AN,
                titre="Nouvelle lecture",
                texte=Texte(
                    uid="PRJLANR5L15B0387",
                    type_=TypeTexte.PROJET,
                    numero=387,
                    titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                    titre_court="PLFSS pour 2018",
                    date_depot=date(2017, 11, 21),
                ),
            ),
            "PRJLSNR5S299B0121": Lecture(
                chambre=Chambre.SENAT,
                titre="Nouvelle lecture",
                texte=Texte(
                    uid="PRJLSNR5S299B0121",
                    type_=TypeTexte.PROJET,
                    numero=121,
                    titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                    titre_court="PLFSS pour 2018",
                    date_depot=date(2017, 11, 30),
                ),
            ),
            "PRJLANR5L15B0434": Lecture(
                chambre=Chambre.AN,
                titre="Lecture définitive",
                texte=Texte(
                    uid="PRJLANR5L15B0434",
                    type_=TypeTexte.PROJET,
                    numero=434,
                    titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                    titre_court="PLFSS pour 2018",
                    date_depot=date(2017, 12, 1),
                ),
            ),
        },
    )
