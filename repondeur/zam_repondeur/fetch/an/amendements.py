import logging
from collections import OrderedDict
from http import HTTPStatus
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


logger = logging.getLogger(__name__)


BASE_URL = "http://www.assemblee-nationale.fr"

# Deprecation warning: this API for fetching amendements will be removed in the future
# and has no Service Level Agreement (SLA)
PATTERN_LISTE = "/{legislature}/amendements/{texte}/{organe_abrev}/liste.xml"
PATTERN_AMENDEMENT = (
    "/{legislature}/xml/amendements/{texte}/{organe_abrev}/{numero}.xml"
)


def aspire_an(lecture: Lecture) -> Tuple[List[Amendement], int, List[str]]:
    logger.info("Récupération des amendements sur %r", lecture)
    try:
        amendements, created, errored = fetch_and_parse_all(lecture=lecture)
    except NotFound:
        return [], 0, []

    return amendements, created, errored


def fetch_and_parse_all(lecture: Lecture) -> Tuple[List[Amendement], int, List[str]]:
    amendements_raw = fetch_amendements(lecture)
    amendements = []
    index = 1
    created = 0
    errored = []
    for item in amendements_raw:
        try:
            amendement, created_ = fetch_amendement(
                lecture=lecture, numero=item["@numero"], position=index
            )
            created += int(created_)
        except NotFound:
            logger.warning("Could not find amendement %r", item["@numero"])
            errored.append(item["@numero"])
            continue
        amendements.append(amendement)
        index += 1
    return amendements, created, errored


def _retrieve_content(url: str) -> Dict[str, OrderedDict]:
    logger.info("Récupération de %r", url)
    resp = cached_session.get(url)
    if resp.status_code == HTTPStatus.NOT_FOUND:
        raise NotFound(url)

    result: OrderedDict = xmltodict.parse(resp.content)
    return result


def fetch_amendements(lecture: Lecture) -> List[OrderedDict]:
    """
    Récupère la liste des références aux amendements, dans l'ordre de dépôt.
    """
    organe_abrev = get_organe_abrev(lecture.organe)
    url = build_url(
        legislature=int(lecture.session),
        texte=lecture.num_texte,
        organe_abrev=organe_abrev,
    )
    content = _retrieve_content(url)
    amendements_raw: List[OrderedDict] = (
        content["amdtsParOrdreDeDiscussion"].get("amendements", [])["amendement"]
    )
    return amendements_raw


def _retrieve_amendement(lecture: Lecture, numero: int) -> OrderedDict:
    organe_abrev = get_organe_abrev(lecture.organe)
    url = build_url(
        legislature=int(lecture.session),
        texte=lecture.num_texte,
        numero=numero,
        organe_abrev=organe_abrev,
    )
    content = _retrieve_content(url)
    return content["amendement"]


def fetch_amendement(
    lecture: Lecture, numero: int, position: int
) -> Tuple[Amendement, bool]:
    """
    Récupère un amendement depuis son numéro.
    """
    logger.info("Récupération de l'amendement %r", numero)
    amend = _retrieve_amendement(lecture, numero)
    subdiv = parse_division(amend["division"])
    article, created = get_one_or_create(
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
        parent, created = get_one_or_create(
            DBSession,
            Amendement,
            lecture=lecture,
            num=parent_num,
            create_method_kwargs={"article": article, "rectif": parent_rectif},
        )
    else:
        parent = None
    amendement, created = get_one_or_create(
        DBSession,
        Amendement,
        lecture=lecture,
        num=int(amend["numero"]),
        create_method_kwargs={"article": article},
    )
    amendement.sort = get_sort(amend)
    amendement.position = position
    amendement.matricule = amend["auteur"]["tribunId"]
    amendement.groupe = get_groupe(amend)
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


def get_organe_abrev(organe: str) -> str:
    from zam_repondeur.data import get_data

    data = get_data("organes")[organe]
    abrev: str = data["libelleAbrev"]
    return abrev


def get_auteur(amendement: OrderedDict) -> str:
    if int(amendement["auteur"]["estGouvernement"]):
        return "LE GOUVERNEMENT"
    return f"{amendement['auteur']['nom']} {amendement['auteur']['prenom']}"


def get_groupe(amendement: OrderedDict) -> str:
    from zam_repondeur.data import get_data

    auteur = amendement["auteur"]
    if int(auteur["estGouvernement"]) or "@xsi:nil" in auteur["groupeTribunId"]:
        return ""
    groupes = get_data("organes")
    groupe = groupes[f"PO{auteur['groupeTribunId']}"]
    libelle: str = groupe["libelle"]
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
