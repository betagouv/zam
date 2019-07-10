from json import load
from typing import Any, Dict, List, Tuple

from .common import extract_from_remote_zip


def get_organes_acteurs() -> Tuple[Dict[str, dict], Dict[str, dict]]:
    data = fetch_organes_acteurs()
    organes_data: List[Dict[str, Any]] = [
        dict_["organe"]
        for filename, dict_ in data.items()
        if filename.startswith("json/organe")
    ]
    organes = extract_organes(organes_data)
    acteurs_data: List[Dict[str, Any]] = [
        dict_["acteur"]
        for filename, dict_ in data.items()
        if filename.startswith("json/acteur")
    ]
    acteurs = extract_acteurs(acteurs_data)
    return organes, acteurs


def fetch_organes_acteurs() -> Dict[str, Any]:
    url = (
        "http://data.assemblee-nationale.fr/static/openData/repository/15/amo/"
        "tous_acteurs_mandats_organes_xi_legislature/"
        "AMO30_tous_acteurs_tous_mandats_tous_organes_historique.json.zip"
    )
    return {
        filename: load(json_file)
        for filename, json_file in extract_from_remote_zip(url)
        if filename.endswith(".json")
    }


def extract_organes(organes: List[dict]) -> Dict[str, dict]:
    return {organe["uid"]: organe for organe in organes}


def extract_acteurs(acteurs: List[dict]) -> Dict[str, dict]:
    return {acteur["uid"]["#text"]: acteur for acteur in acteurs}
