from http import HTTPStatus

import requests

URL = "https://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv"


def fetch_senateurs() -> bytes:
    resp = requests.get(URL)
    if resp.status_code != HTTPStatus.OK:  # 200
        raise RuntimeError("Failed to download senateurs CSV file")
    return resp.content
