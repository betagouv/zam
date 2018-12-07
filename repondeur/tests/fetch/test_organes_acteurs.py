import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest


HERE = Path(os.path.dirname(__file__))

SAMPLE_DATA = HERE / "sample_data"

ORGANES_ACTEURS = SAMPLE_DATA / "AMO10_deputes_actifs_mandats_actifs_organes_XV.json"


@pytest.fixture(scope="session")
def sample_data():
    with open(ORGANES_ACTEURS) as f_:
        data = json.load(f_)
    return data


def test_get_organes_acteurs(sample_data):
    from zam_repondeur.fetch.an.organes_acteurs import get_organes_acteurs

    with patch(
        "zam_repondeur.fetch.an.organes_acteurs.fetch_organes_acteurs",
        return_value=sample_data,
    ):
        organes, acteurs = get_organes_acteurs()

    assert len(organes) == 5
    assert organes["PO717460"]["libelleAbrege"] == "Assemblée"
    assert organes["PO717460"]["libelleAbrev"] == "AN"

    assert len(acteurs) == 1
    assert "PA718838" in acteurs


def test_extract_organes(sample_data):
    from zam_repondeur.fetch.an.organes_acteurs import extract_organes

    organes = extract_organes(sample_data)

    assert len(organes) == 5
    assert organes["PO717460"]["libelleAbrege"] == "Assemblée"
    assert organes["PO717460"]["libelleAbrev"] == "AN"


def test_extract_acteurs(sample_data):
    from zam_repondeur.fetch.an.organes_acteurs import extract_acteurs

    acteurs = extract_acteurs(sample_data)

    assert len(acteurs) == 1
    assert "PA718838" in acteurs
