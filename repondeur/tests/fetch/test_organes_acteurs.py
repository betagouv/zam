import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

HERE = Path(os.path.dirname(__file__))
ORGANES_ACTEURS = (
    HERE
    / "sample_data"
    / "AMO30_tous_acteurs_tous_mandats_tous_organes_historique.json.zip"
)


@pytest.fixture(scope="session")
def sample_data():
    from zam_repondeur.fetch.an.common import extract_from_zip

    with open(ORGANES_ACTEURS, "rb") as f_:
        data = {
            filename: json.load(json_file)
            for filename, json_file in extract_from_zip(f_)
        }
    return data


def test_get_organes_acteurs(sample_data):
    from zam_repondeur.fetch.an.organes_acteurs import get_organes_acteurs

    with patch(
        "zam_repondeur.fetch.an.organes_acteurs.fetch_organes_acteurs",
        return_value=sample_data,
    ):
        organes, acteurs = get_organes_acteurs()

    assert len(organes) == 1216
    assert organes["PO717460"]["libelleAbrege"] == "Assemblée"
    assert organes["PO717460"]["libelleAbrev"] == "AN"

    assert len(acteurs) == 577
    assert "PA718838" in acteurs


def test_extract_organes(sample_data):
    from zam_repondeur.fetch.an.organes_acteurs import extract_organes

    organes = extract_organes(
        dict_["organe"]
        for filename, dict_ in sample_data.items()
        if filename.startswith("json/organe")
    )

    assert len(organes) == 1216
    assert organes["PO717460"]["libelleAbrege"] == "Assemblée"
    assert organes["PO717460"]["libelleAbrev"] == "AN"


def test_extract_acteurs(sample_data):
    from zam_repondeur.fetch.an.organes_acteurs import extract_acteurs

    acteurs = extract_acteurs(
        dict_["acteur"]
        for filename, dict_ in sample_data.items()
        if filename.startswith("json/acteur")
    )

    assert len(acteurs) == 577
    assert "PA718838" in acteurs
