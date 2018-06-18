import json
import os
from collections import OrderedDict
from http import HTTPStatus
from pathlib import Path
from typing import List, Tuple

import xmltodict

from ..exceptions import NotFound
from ..http import cached_session
from .models import Amendement
from .parser import _parse_subdiv


BASE_URL = "http://www.assemblee-nationale.fr"


def build_url(legislature: int, texte: str, numero: int = 0) -> str:
    if numero:
        pattern = os.environ["ZAM_AN_PATTERN_AMENDEMENT"]
        path = pattern.format(legislature=legislature, texte=texte, numero=numero)
    else:
        pattern = os.environ["ZAM_AN_PATTERN_LISTE"]
        path = pattern.format(legislature=legislature, texte=texte)
    return f"{BASE_URL}{path}"


def get_auteur(amendement: OrderedDict) -> str:
    if int(amendement["auteur"]["estGouvernement"]):
        return "LE GOUVERNEMENT"
    return f"{amendement['auteur']['nom']} {amendement['auteur']['prenom']}"


def get_groupe(amendement: OrderedDict, groups_folder: Path) -> str:
    auteur = amendement["auteur"]
    if int(auteur["estGouvernement"]) or "@xsi:nil" in auteur["groupeTribunId"]:
        return ""
    groupe_raw = (groups_folder / f"PO{auteur['groupeTribunId']}.json").read_text()
    libelle: str = json.loads(groupe_raw)["organe"]["libelle"]
    return libelle


def unjustify(content: str) -> str:
    return content.replace(' style="text-align: justify;"', "")


def fetch_amendement(
    legislature: int, texte: str, numero: int, groups_folder: Path
) -> Amendement:
    """
    Récupère un amendement depuis son numéro.
    """
    url = build_url(legislature, texte, numero)

    resp = cached_session.get(url)
    if resp.status_code == HTTPStatus.NOT_FOUND:  # 404
        raise NotFound(url)

    content = xmltodict.parse(resp.content)
    amendement = content["amendement"]
    subdiv_type, subdiv_num, subdiv_mult, subdiv_pos = _parse_subdiv(
        amendement["division"]["titre"]
    )
    if amendement["division"]["avantApres"]:
        subdiv_pos = amendement["division"]["avantApres"].lower()
        if subdiv_pos == "a":  # TODO: understand what it means...
            subdiv_pos = ""
    return Amendement(  # type: ignore
        chambre="an",
        session=str(legislature),
        num_texte=texte,
        num=amendement["numero"],
        subdiv_type=subdiv_type,
        subdiv_num=subdiv_num,
        subdiv_mult=subdiv_mult,
        subdiv_pos=subdiv_pos,
        sort=amendement["sortEnSeance"].lower(),
        matricule=amendement["auteur"]["tribunId"],
        groupe=get_groupe(amendement, groups_folder),
        auteur=get_auteur(amendement),
        dispositif=unjustify(amendement["dispositif"]),
        objet=unjustify(amendement["exposeSommaire"]),
    )


def fetch_amendements(legislature: int, texte: str) -> Tuple[str, List[OrderedDict]]:
    """
    Récupère la liste des références aux amendements, dans l'ordre de dépôt.
    """
    url = build_url(legislature, texte)

    resp = cached_session.get(url)
    if resp.status_code == HTTPStatus.NOT_FOUND:  # 404
        raise NotFound(url)

    content = xmltodict.parse(resp.content)
    amendements_raw = content["amdtsParOrdreDeDiscussion"]["amendements"]["amendement"]
    title = content["amdtsParOrdreDeDiscussion"]["@titre"]
    return title, amendements_raw


def fetch_and_parse_all(
    legislature: int, texte: str, groups_folder: Path
) -> Tuple[str, List[Amendement]]:
    title, amendements_raw = fetch_amendements(legislature, texte)
    return (
        title,
        [
            fetch_amendement(legislature, texte, item["@numero"], groups_folder)
            for item in amendements_raw
        ],
    )
