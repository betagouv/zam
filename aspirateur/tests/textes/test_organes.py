import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest


HERE = Path(os.path.dirname(__file__))

ORGANES = (
    HERE.parent / "sample_data" / "AMO10_deputes_actifs_mandats_actifs_organes_XV.json"
)


@pytest.fixture(scope="session")
def sample_data():
    with open(ORGANES) as f_:
        data = json.load(f_)
    return data


def test_get_organes(sample_data):
    from zam_aspirateur.textes.organes import get_organes

    with patch("zam_aspirateur.textes.organes.fetch_organes", return_value=sample_data):
        organes = get_organes(legislature=15)

    assert len(organes) == 4
    assert organes["PO717460"]["libelleAbrege"] == "Assemblée"
    assert organes["PO717460"]["libelleAbrev"] == "AN"


def test_parse_organes(sample_data):
    from zam_aspirateur.textes.organes import parse_organes

    organes = parse_organes(sample_data["export"])

    assert len(organes) == 4
    assert organes["PO717460"]["libelleAbrege"] == "Assemblée"
    assert organes["PO717460"]["libelleAbrev"] == "AN"
