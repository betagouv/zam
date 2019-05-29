from http import HTTPStatus
from typing import List

import requests


URL = "https://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv"


def fetch_senateurs() -> List[str]:
    resp = requests.get(URL)
    if resp.status_code != HTTPStatus.OK:  # 200
        raise RuntimeError("Failed to download senateurs CSV file")

    text = resp.content.decode("cp1252")
    lines = text.splitlines()
    return lines
