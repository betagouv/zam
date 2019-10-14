from http import HTTPStatus

from zam_repondeur.services.fetch.http import cached_session

URL = "https://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv"


def fetch_senateurs() -> bytes:
    resp = cached_session.get(URL)
    if resp.status_code != HTTPStatus.OK:  # 200
        raise RuntimeError("Failed to download senateurs CSV file")
    content: bytes = resp.content
    return content
