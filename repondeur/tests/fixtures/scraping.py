from unittest.mock import patch
from pathlib import Path

import pytest


HERE = Path(__file__)
SAMPLE_DATA_DIR = HERE.parent / "sample_data" / "senat"


@pytest.yield_fixture(scope="session", autouse=True)
def mock_scraping_senat():
    filename = SAMPLE_DATA_DIR / "textes-recents.html"
    with patch("zam_repondeur.fetch.senat.scraping.download_textes_recents") as dl:
        with open(filename, "r", encoding="utf-8-sig") as f_:
            dl.return_value = f_.read()
        yield
