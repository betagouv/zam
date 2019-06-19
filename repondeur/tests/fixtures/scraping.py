from pathlib import Path

import pytest
import responses


HERE = Path(__file__)
SAMPLE_DATA_DIR = HERE.parent.parent / "fetch" / "sample_data" / "senat"


@pytest.fixture(scope="session", autouse=True)
def mock_scraping_senat():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as mock_resp:
        mock_resp.add(
            responses.GET,
            "http://www.senat.fr/dossiers-legislatifs/textes-recents.html",
            body=(SAMPLE_DATA_DIR / "textes-recents.html").read_bytes(),
            status=200,
        )
        for path in SAMPLE_DATA_DIR.glob("dosleg*.xml"):
            mock_resp.add(
                responses.GET,
                f"http://www.senat.fr/dossier-legislatif/rss/{path.name}",
                body=path.read_bytes(),
                status=200,
            )
        yield
