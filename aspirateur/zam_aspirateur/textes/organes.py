from json import load
from typing import Dict

from .common import extract_from_remote_zip, roman


def get_organes(legislature: int) -> Dict[str, dict]:
    data = fetch_organes(legislature)
    organes = parse_organes(data["export"])
    return organes


def fetch_organes(legislature: int) -> dict:
    legislature_roman = roman(legislature)
    filename = f"AMO10_deputes_actifs_mandats_actifs_organes_{legislature_roman}.json"
    url = f"http://data.assemblee-nationale.fr/static/openData/repository/{legislature}/amo/deputes_actifs_mandats_actifs_organes/{filename}.zip"  # noqa
    with extract_from_remote_zip(url, filename) as json_file:
        data: dict = load(json_file)
    return data


def parse_organes(data: dict) -> Dict[str, dict]:
    return {organe["uid"]: organe for organe in data["organes"]["organe"]}
