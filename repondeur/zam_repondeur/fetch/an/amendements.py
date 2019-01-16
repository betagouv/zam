import logging
import re
from collections import OrderedDict
from datetime import datetime
from http import HTTPStatus
from typing import Dict, List, Optional, Set, Tuple, Union
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
from .division import parse_avant_apres


logger = logging.getLogger(__name__)


BASE_URL = "http://www.assemblee-nationale.fr"

# Deprecation warning: this API for fetching amendements will be removed in the future
# and has no Service Level Agreement (SLA)
PATTERN_LISTE = "/{legislature}/amendements/{texte}{suffixe}/{organe_abrev}/liste.xml"
PATTERN_AMENDEMENT = (
    "/{legislature}/xml/amendements/"
    "{texte}{suffixe}/{organe_abrev}/{numero_prefixe}.xml"
)


class OrganeNotFound(Exception):
    def __init__(self, organe: str) -> None:
        super().__init__(f"Organe {organe} not found in data")
        self.organe = organe


def aspire_an(lecture: Lecture) -> Tuple[List[Amendement], int, List[str]]:
    logger.info("Récupération des amendements sur %r", lecture)
    try:
        amendements, created, errored = fetch_and_parse_all(lecture=lecture)
    except NotFound:
        return [], 0, []

    return amendements, created, errored


def fetch_and_parse_all(lecture: Lecture) -> Tuple[List[Amendement], int, List[str]]:
    amendements: List[Amendement] = []
    created = 0
    errored: List[str] = []

    discussion_items = fetch_discussion_list(lecture)
    if not discussion_items:
        logger.warning("Could not find amendements from %r", lecture)

    reset_amendements_positions(lecture, discussion_items)

    amendements_disc, created_disc, errored_disc = _fetch_amendements_discussed(
        lecture, discussion_items
    )

    amendements_other, created_other, errored_other = _fetch_amendements_other(
        lecture=lecture,
        discussion_nums={parse_num_in_liste(d["@numero"])[1] for d in discussion_items},
        prefix=find_prefix(discussion_items, lecture),
    )

    amendements = amendements_disc + amendements_other
    created = created_disc + created_other
    errored = errored_disc + errored_other

    return amendements, created, errored


def reset_amendements_positions(
    lecture: Lecture, discussion_items: List[OrderedDict]
) -> None:

    current_order = {
        amdt.num: amdt.position
        for amdt in lecture.amendements
        if amdt.position is not None
    }

    new_order = {
        parse_num_in_liste(item["@numero"])[1]: index
        for index, item in enumerate(discussion_items, start=1)
    }

    # Reset position for all amendements that moved,
    # so that we don't break the UNIQUE INDEX constraint later
    for amdt in lecture.amendements:
        if amdt.num not in current_order:
            continue
        if new_order.get(amdt.num) != current_order[amdt.num]:
            amdt.position = None
        if amdt.num not in new_order:  # removed
            logger.info("Amendement %s retiré de la discussion", amdt.num)
    DBSession.flush()


def find_prefix(discussion_items: List[OrderedDict], lecture: Lecture) -> str:
    if discussion_items:
        numero_prefixe = discussion_items[0]["@numero"]
        prefix, _ = parse_num_in_liste(numero_prefixe)
        return prefix
    return get_organe_prefix(lecture.organe)


def get_organe_prefix(organe: str) -> str:
    abrev = get_organe_abrev(organe)
    return _ORGANE_PREFIX.get(abrev, "")


_ORGANE_PREFIX = {
    "CION_FIN": "CF",  # Finances
    "CION-SOC": "AS",  # Affaires sociales
    "CION-CEDU": "AC",  # Affaires culturelles et éducation
    "CION-ECO": "CE",  # Affaires économiques
    "CION_AFETR": "AE",  # Affaires étrangères
    "CION_DEF": "DN",  # Défense
    "CION_LOIS": "CL",  # Lois
    "CION-DVP": "CD",  # Développement durable
}


def _fetch_amendements_discussed(
    lecture: Lecture, discussion_items: List[OrderedDict]
) -> Tuple[List[Amendement], int, List[str]]:
    amendements: List[Amendement] = []
    created = 0
    errored: List[str] = []

    for position, item in enumerate(discussion_items, start=1):
        numero_prefixe = item["@numero"]
        id_discussion_commune = (
            int(item["@discussionCommune"]) if item["@discussionCommune"] else None
        )
        id_identique = (
            int(item["@discussionIdentique"]) if item["@discussionIdentique"] else None
        )
        try:
            amendement, created_ = fetch_amendement(
                lecture=lecture,
                numero_prefixe=numero_prefixe,
                position=position,
                id_discussion_commune=id_discussion_commune,
                id_identique=id_identique,
            )
        except NotFound:
            prefix, num = parse_num_in_liste(numero_prefixe)
            logger.warning("Could not find amendement %r", num)
            errored.append(str(num))
            continue
        except Exception:
            prefix, num = parse_num_in_liste(numero_prefixe)
            logger.exception("Error while fetching amendement %r", num)
            errored.append(str(num))
            continue
        amendements.append(amendement)
        created += int(created_)
    return amendements, created, errored


def _fetch_amendements_other(
    lecture: Lecture, discussion_nums: Set[int], prefix: str
) -> Tuple[List[Amendement], int, List[str]]:
    amendements: List[Amendement] = []
    created = 0
    errored: List[str] = []

    max_num_seen = max(discussion_nums) if discussion_nums else 0
    numero = 0

    # We can't try all possible numbers, so we'll stop after a string of 404s
    while numero < (max_num_seen + 20):
        numero += 1
        if numero in discussion_nums:
            continue
        try:
            amendement, created_ = fetch_amendement(
                lecture=lecture,
                numero_prefixe=f"{prefix}{numero}",
                position=None,
                id_discussion_commune=None,
                id_identique=None,
            )
        except NotFound:
            continue
        except Exception:
            logger.exception("Error while fetching amendement %r", numero)
            errored.append(str(numero))
            continue
        amendements.append(amendement)
        created += int(created_)
        if numero > max_num_seen:
            max_num_seen = numero
    return amendements, created, errored


def _retrieve_content(url: str) -> Dict[str, OrderedDict]:
    logger.info("Récupération de %r", url)
    resp = cached_session.get(url)
    if resp.status_code == HTTPStatus.NOT_FOUND:
        raise NotFound(url)

    result: OrderedDict = xmltodict.parse(resp.content)
    return result


def fetch_discussion_list(lecture: Lecture) -> List[OrderedDict]:
    """
    Récupère la liste ordonnée des amendements soumis à la discussion.

    Les amendements irrecevables ou encore en traitement ne sont pas inclus.
    """
    url = build_url(lecture)
    content = _retrieve_content(url)

    try:
        # If there is only 1 amendement, xmltodict does not return a list :(
        discussed_amendements: Union[OrderedDict, List[OrderedDict]] = (
            content["amdtsParOrdreDeDiscussion"]["amendements"]["amendement"]
        )
    except TypeError:
        return []

    if isinstance(discussed_amendements, OrderedDict):
        return [discussed_amendements]
    return discussed_amendements


def _retrieve_amendement(lecture: Lecture, numero_prefixe: str) -> OrderedDict:
    url = build_url(lecture, numero_prefixe)
    content = _retrieve_content(url)
    return content["amendement"]


def fetch_amendement(
    lecture: Lecture,
    numero_prefixe: str,
    position: Optional[int],
    id_discussion_commune: Optional[int] = None,
    id_identique: Optional[int] = None,
) -> Tuple[Amendement, bool]:
    """
    Récupère un amendement depuis son numéro.
    """
    logger.info("Récupération de l'amendement %r", numero_prefixe)
    amend = _retrieve_amendement(lecture, numero_prefixe)
    article = _get_article(lecture, amend["division"])
    parent = _get_parent(lecture, article, amend)
    amendement, created = _create_or_update_amendement(
        lecture, article, parent, amend, position, id_discussion_commune, id_identique
    )
    return amendement, created


def _get_article(lecture: Lecture, division: dict) -> Article:
    subdiv = parse_division(division)
    article: Article
    created: bool
    article, created = get_one_or_create(
        Article,
        lecture=lecture,
        type=subdiv.type_,
        num=subdiv.num,
        mult=subdiv.mult,
        pos=subdiv.pos,
    )
    return article


def _get_parent(
    lecture: Lecture, article: Article, amend: OrderedDict
) -> Optional[Amendement]:
    parent_num, parent_rectif = Amendement.parse_num(get_parent_raw_num(amend))
    parent: Optional[Amendement]
    if parent_num:
        parent, created = get_one_or_create(
            Amendement,
            create_kwargs={"article": article, "rectif": parent_rectif},
            lecture=lecture,
            num=parent_num,
        )
    else:
        parent = None
    return parent


def _create_or_update_amendement(
    lecture: Lecture,
    article: Optional[Article],
    parent: Optional[Amendement],
    amend: OrderedDict,
    position: Optional[int],
    id_discussion_commune: Optional[int],
    id_identique: Optional[int],
) -> Tuple[Amendement, bool]:
    amendement, created = get_one_or_create(
        Amendement,
        create_kwargs={"article": article, "parent": parent},
        lecture=lecture,
        num=int(amend["numero"]),
    )

    raw_auteur = amend.get("auteur")
    if not raw_auteur:
        logger.warning("Unknown auteur for amendement %s", amend["numero"])
        matricule, groupe, auteur = "", "", ""
    else:
        matricule = raw_auteur["tribunId"]
        groupe = get_groupe(raw_auteur, amendement.num)
        auteur = get_auteur(raw_auteur)

    attributes = {
        "rectif": get_rectif(amend),
        "article": article,
        "parent": parent,
        "sort": get_sort(amend),
        "position": position,
        "id_discussion_commune": id_discussion_commune,
        "id_identique": id_identique,
        "matricule": matricule,
        "groupe": groupe,
        "auteur": auteur,
        "corps": unjustify(get_str_or_none(amend, "dispositif") or ""),
        "expose": unjustify(get_str_or_none(amend, "exposeSommaire") or ""),
    }

    modified = False
    for name, value in attributes.items():
        if getattr(amendement, name) != value:
            setattr(amendement, name, value)
            modified = True

    if not created and modified:
        amendement.modified_at = datetime.utcnow()

    DBSession.flush()  # make sure foreign keys are updated

    return amendement, created


def build_url(lecture: Lecture, numero_prefixe: str = "") -> str:

    legislature = int(lecture.session)
    texte = f"{lecture.num_texte:04}"

    # The 1st "lecture" of the "projet de loi de finances" (PLF) has two parts
    if lecture.partie == 1:
        suffixe = "A"
    elif lecture.partie == 2:
        suffixe = "C"
    else:
        suffixe = ""

    organe_abrev = get_organe_abrev(lecture.organe)

    if numero_prefixe:
        path = PATTERN_AMENDEMENT.format(
            legislature=legislature,
            texte=texte,
            suffixe=suffixe,
            organe_abrev=organe_abrev,
            numero_prefixe=numero_prefixe,
        )
    else:
        path = PATTERN_LISTE.format(
            legislature=legislature,
            texte=texte,
            suffixe=suffixe,
            organe_abrev=organe_abrev,
        )

    url: str = urljoin(BASE_URL, path)
    return url


def get_organe_abrev(organe: str) -> str:
    from zam_repondeur.data import get_data

    try:
        data = get_data("organes")[organe]
        abrev: str = data["libelleAbrev"]
        return abrev
    except KeyError:
        raise OrganeNotFound(organe)


def parse_num_in_liste(num_long: str) -> Tuple[str, int]:
    mo = _RE_NUM.match(num_long)
    if mo is None:
        raise ValueError(f"Cannot parse amendement number {num_long!r}")
    return mo.group("acronyme"), int(mo.group("num"))


_RE_NUM = re.compile(r"(?P<acronyme>[A-Z]*)(?P<num>\d+)")


def get_auteur(raw_auteur: OrderedDict) -> str:
    if int(raw_auteur["estGouvernement"]):
        return "LE GOUVERNEMENT"
    return f"{raw_auteur['nom']} {raw_auteur['prenom']}"


def get_groupe(raw_auteur: OrderedDict, amendement_num: int) -> str:
    from zam_repondeur.data import get_data

    gouvernemental = bool(int(raw_auteur["estGouvernement"]))
    groupe_tribun_id = get_str_or_none(raw_auteur, "groupeTribunId")
    if gouvernemental or (groupe_tribun_id is None):
        return ""
    groupes = get_data("organes")
    try:
        groupe_tribun_id = f"PO{raw_auteur['groupeTribunId']}"
    except KeyError:
        logger.error(
            "Unknown groupe %r for amendement %s", groupe_tribun_id, amendement_num
        )
        return ""
    try:
        groupe: Dict[str, str] = groupes[groupe_tribun_id]
    except KeyError:
        logger.error(
            "Unknown groupe tribun %r in groupes for amendement %s",
            groupe_tribun_id,
            amendement_num,
        )
        return ""
    return groupe["libelle"]


ETATS_OK = {
    "AT",  # à traiter
    "T",  # traité
    "ER",  # en recevabilité
    "R",  # recevable
    "AC",  # à discuter
    "DI",  # discuté
}


def get_sort(amendement: OrderedDict) -> str:
    sort = get_str_or_none(amendement, "sortEnSeance")
    if sort is not None:
        return sort.lower()
    if (
        amendement["retireAvantPublication"] == "1"
        or amendement.get("retireApresPublication", "0") == "1"
    ):
        return "Retiré"
    etat = get_str_or_none(amendement, "etat")
    if etat not in ETATS_OK:
        return "Irrecevable"
    return ""


def get_parent_raw_num(amendement: OrderedDict) -> str:
    return get_str_or_none(amendement, "numeroParent") or ""


def get_rectif(amendement: OrderedDict) -> int:
    return parse_numero_long_with_rect(amendement["numeroLong"])


RE_NUM_LONG = re.compile(
    r"""
    (?P<prefix>[A-Z]*)
    (?P<num>\d+)
    (?P<rect>\s\((?:(?P<rect_mult>\d+)\w+\s)?Rect\))?
    """,
    re.VERBOSE,
)


def parse_numero_long_with_rect(text: str) -> int:
    mo = RE_NUM_LONG.match(text)
    if mo is not None and mo.group("rect"):
        return int(mo.group("rect_mult") or 1)
    return 0


def get_str_or_none(amendement: OrderedDict, key: str) -> Optional[str]:
    value = amendement[key]
    if isinstance(value, str):
        return value
    if isinstance(value, OrderedDict) and value.get("@xsi:nil") == "true":
        return None
    raise ValueError(f"Unexpected value {value!r} for key {key!r}")


def unjustify(content: str) -> str:
    return content.replace(' style="text-align: justify;"', "")


def parse_division(division: dict) -> SubDiv:
    if division["type"] == "TITRE":
        return SubDiv("titre", "", "", "")
    if division["type"] == "ARTICLE":
        subdiv = _parse_subdiv(division["titre"])
    else:
        subdiv = _parse_subdiv(division["divisionRattache"])
    if division["avantApres"]:
        pos = parse_avant_apres(division["avantApres"])
        subdiv = subdiv._replace(pos=pos)
    return subdiv
