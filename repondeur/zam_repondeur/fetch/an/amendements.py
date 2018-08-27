import json
from collections import OrderedDict
from http import HTTPStatus
from pathlib import Path
from typing import Dict, List, Tuple, Union
from urllib.parse import urljoin

import xmltodict

from zam_repondeur.fetch.division import _parse_subdiv
from zam_repondeur.fetch.exceptions import NotFound
from zam_repondeur.fetch.http import cached_session
from zam_repondeur.fetch.division import SubDiv
from zam_repondeur.models import (
    DBSession,
    Article,
    Amendement,
    Lecture,
    get_one_or_create,
)


BASE_URL = "http://www.assemblee-nationale.fr"

# Deprecation warning: this API for fetching amendements will be removed in the future
# and has no Service Level Agreement (SLA)
PATTERN_LISTE = "/{legislature}/amendements/{texte}/{organe_abrev}/liste.xml"
PATTERN_AMENDEMENT = (
    "/{legislature}/xml/amendements/{texte}/{organe_abrev}/{numero}.xml"
)


def aspire_an(
    lecture: Lecture, groups_folder: Path
) -> Tuple[List[Amendement], int, List[str]]:
    print("Récupération du titre et des amendements déposés...")
    try:
        amendements, created, errored = fetch_and_parse_all(
            lecture=lecture, groups_folder=groups_folder
        )
    except NotFound:
        return [], 0, []

    return amendements, created, errored


def fetch_and_parse_all(
    lecture: Lecture, groups_folder: Path
) -> Tuple[List[Amendement], int, List[str]]:
    amendements_raw = fetch_amendements(lecture, groups_folder)
    amendements = []
    index = 1
    created = 0
    errored = []
    for item in amendements_raw:
        try:
            amendement, created_ = fetch_amendement(
                lecture=lecture,
                numero=item["@numero"],
                groups_folder=groups_folder,
                position=index,
            )
            created += int(created_)
        except NotFound:
            errored.append(item["@numero"])
            continue
        amendements.append(amendement)
        index += 1
    return amendements, created, errored


def _retrieve_content(url: str) -> Dict[str, OrderedDict]:
    resp = cached_session.get(url)
    if resp.status_code == HTTPStatus.NOT_FOUND:
        raise NotFound(url)

    result: OrderedDict = xmltodict.parse(resp.content)
    return result


def fetch_amendements(lecture: Lecture, groups_folder: Path) -> List[OrderedDict]:
    """
    Récupère la liste des références aux amendements, dans l'ordre de dépôt.
    """
    organe_abrev = get_organe_abrev(lecture.organe, groups_folder)
    url = build_url(
        legislature=int(lecture.session),
        texte=lecture.num_texte,
        organe_abrev=organe_abrev,
    )
    content = _retrieve_content(url)
    amendements_raw: List[OrderedDict] = content["amdtsParOrdreDeDiscussion"][
        "amendements"
    ]["amendement"]
    return amendements_raw


def _retrieve_amendement(
    lecture: Lecture, numero: int, groups_folder: Path
) -> OrderedDict:
    organe_abrev = get_organe_abrev(lecture.organe, groups_folder)
    url = build_url(
        legislature=int(lecture.session),
        texte=lecture.num_texte,
        numero=numero,
        organe_abrev=organe_abrev,
    )
    content = _retrieve_content(url)
    return content["amendement"]


def fetch_amendement(
    lecture: Lecture, numero: int, groups_folder: Path, position: int
) -> Tuple[Amendement, bool]:
    """
    Récupère un amendement depuis son numéro.
    """
    amend = _retrieve_amendement(lecture, numero, groups_folder)
    subdiv = parse_division(amend["division"])
    article, created = get_one_or_create(  # type: ignore
        DBSession,
        Article,
        lecture=lecture,
        type=subdiv.type_,
        num=subdiv.num,
        mult=subdiv.mult,
        pos=subdiv.pos,
    )
    parent_num, parent_rectif = Amendement.parse_num(get_parent_raw_num(amend))
    if parent_num:
        parent, created = get_one_or_create(  # type: ignore
            DBSession,
            Amendement,
            lecture=lecture,
            article=article,
            num=parent_num,
            rectif=parent_rectif,
        )
    else:
        parent = None
    amendement, created = get_one_or_create(  # type: ignore
        DBSession,
        Amendement,
        lecture=lecture,
        article=article,
        num=int(amend["numero"]),
    )
    amendement.sort = get_sort(amend)
    amendement.position = position
    amendement.matricule = amend["auteur"]["tribunId"]
    amendement.groupe = get_groupe(amend, groups_folder)
    amendement.auteur = get_auteur(amend)
    amendement.parent = parent
    amendement.dispositif = unjustify(amend["dispositif"])
    amendement.objet = unjustify(amend["exposeSommaire"])
    return amendement, created


def build_url(
    legislature: int, texte: int, numero: int = 0, organe_abrev: str = "AN"
) -> str:
    if numero:
        path = PATTERN_AMENDEMENT.format(
            legislature=legislature,
            texte=f"{texte:04}",
            organe_abrev=organe_abrev,
            numero=numero,
        )
    else:
        path = PATTERN_LISTE.format(
            legislature=legislature, texte=f"{texte:04}", organe_abrev=organe_abrev
        )
    url: str = urljoin(BASE_URL, path)
    return url


def get_organe_abrev(organe: str, groups_folder: Path) -> str:
    data = json.loads((groups_folder / f"{organe}.json").read_text())
    abrev: str = data["organe"]["libelleAbrev"]
    return abrev


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


def get_sort(amendement: OrderedDict) -> str:
    sort: Union[str, OrderedDict] = amendement["sortEnSeance"]
    if isinstance(sort, OrderedDict):
        if "@xsi:nil" in sort:
            return ""
        else:
            raise NotImplementedError
    return sort.lower()


def get_parent_raw_num(amendement: OrderedDict) -> str:
    parent: Union[str, OrderedDict] = amendement["numeroParent"]
    if isinstance(parent, OrderedDict):
        if "@xsi:nil" in parent:
            return ""
        else:
            raise NotImplementedError
    return parent


def unjustify(content: str) -> str:
    return content.replace(' style="text-align: justify;"', "")


def parse_division(division: dict) -> SubDiv:
    if division["type"] == "TITRE":
        return SubDiv("titre", "", "", "")
    subdiv = _parse_subdiv(division["titre"])
    if division["avantApres"]:
        subdiv = subdiv._replace(pos=division["avantApres"].lower())
        if subdiv.pos == "a":  # TODO: understand what it means...
            subdiv = subdiv._replace(pos="")
    return subdiv
