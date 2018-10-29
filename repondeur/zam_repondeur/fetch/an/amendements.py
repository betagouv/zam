import logging
from collections import OrderedDict
from datetime import datetime
from http import HTTPStatus
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin

import xmltodict

from zam_repondeur.fetch.amendements import clear_position_if_removed
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
    "/{legislature}/xml/amendements/{texte}{suffixe}/{organe_abrev}/{numero}.xml"
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
    clear_position_if_removed(lecture, amendements)
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
    url = build_url(lecture)
    content = _retrieve_content(url)

    # If there is only 1 amendement, xmltodict does not return a list :(
    amendements_raw: Union[OrderedDict, List[OrderedDict]] = (
        content["amdtsParOrdreDeDiscussion"]["amendements"]["amendement"]
    )
    if isinstance(amendements_raw, OrderedDict):
        return [amendements_raw]
    return amendements_raw


def _retrieve_amendement(lecture: Lecture, numero: int) -> OrderedDict:
    url = build_url(lecture, numero)
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
    article = _get_article(lecture, amend["division"])
    parent = _get_parent(lecture, article, amend)
    amendement, created = _create_or_update_amendement(
        lecture, article, parent, amend, position
    )
    return amendement, created


def _get_article(lecture: Lecture, division: dict) -> Article:
    subdiv = parse_division(division)
    article: Article
    created: bool
    article, created = get_one_or_create(
        DBSession,
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
            DBSession,
            Amendement,
            create_method="create",
            create_method_kwargs={"article": article, "rectif": parent_rectif},
            lecture=lecture,
            num=parent_num,
        )
    else:
        parent = None
    return parent


def _create_or_update_amendement(
    lecture: Lecture,
    article: Article,
    parent: Optional[Amendement],
    amend: OrderedDict,
    position: int,
) -> Tuple[Amendement, bool]:
    amendement, created = get_one_or_create(
        DBSession,
        Amendement,
        create_method="create",
        create_method_kwargs={"article": article, "parent": parent},
        lecture=lecture,
        num=int(amend["numero"]),
    )
    if not created:
        amendement.article = article
        amendement.parent = parent

    sort = get_sort(amend)
    matricule = amend["auteur"]["tribunId"]
    groupe = get_groupe(amend)
    auteur = get_auteur(amend)
    dispositif = unjustify(amend["dispositif"])
    objet = unjustify(amend["exposeSommaire"])

    if not created and (
        article != amendement.article
        or parent != amendement.parent
        or sort != amendement.sort
        or position != amendement.position
        or matricule != amendement.matricule
        or groupe != amendement.groupe
        or auteur != amendement.auteur
        or dispositif != amendement.dispositif
        or objet != amendement.objet
    ):
        amendement.modified_at = datetime.utcnow()

    amendement.sort = sort
    amendement.position = position
    amendement.matricule = matricule
    amendement.groupe = groupe
    amendement.auteur = auteur
    amendement.dispositif = dispositif
    amendement.objet = objet
    DBSession.flush()  # make sure foreign keys are updated
    return amendement, created


def build_url(lecture: Lecture, numero: int = 0) -> str:

    legislature = int(lecture.session)
    texte = f"{lecture.num_texte:04}"
    suffixe = "A" if "loi de finances" in lecture.dossier_legislatif else ""
    organe_abrev = get_organe_abrev(lecture.organe)

    if numero:
        path = PATTERN_AMENDEMENT.format(
            legislature=legislature,
            texte=texte,
            suffixe=suffixe,
            organe_abrev=organe_abrev,
            numero=numero,
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
    try:
        groupe_tribun_id = f"PO{auteur['groupeTribunId']}"
    except KeyError:
        logger.error(
            "Unknown groupe %r for amendement %s",
            groupe_tribun_id,
            amendement["numero"],
        )
        return ""
    try:
        groupe: Dict[str, str] = groupes[groupe_tribun_id]
    except KeyError:
        logger.error(
            "Unknown groupe tribun %r in groupes for amendement %s",
            groupe_tribun_id,
            amendement["numero"],
        )
        return ""
    return groupe["libelle"]


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
        pos = parse_avant_apres(division["avantApres"])
        subdiv = subdiv._replace(pos=pos)
    return subdiv
