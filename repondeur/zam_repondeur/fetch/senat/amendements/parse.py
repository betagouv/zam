import re
from typing import Dict, NamedTuple, Optional, Tuple
from urllib.parse import urlparse

from zam_repondeur.clean import clean_html
from zam_repondeur.fetch.dates import parse_date
from zam_repondeur.fetch.division import _parse_subdiv
from zam_repondeur.models import Article, Amendement, Lecture, get_one_or_create


def parse_from_csv(row: dict, lecture: Lecture) -> Tuple[Amendement, bool]:
    subdiv = _parse_subdiv(row["Subdivision "])
    article, created = get_one_or_create(
        Article,
        lecture=lecture,
        type=subdiv.type_,
        num=subdiv.num,
        mult=subdiv.mult,
        pos=subdiv.pos,
    )
    num, rectif = Amendement.parse_num(row["Numéro "])
    amendement, created = get_one_or_create(
        Amendement,
        create_method="create",
        create_method_kwargs={"article": article},
        lecture=lecture,
        num=num,
    )
    if not created:
        amendement.article = article
    amendement.rectif = rectif
    amendement.alinea = row["Alinéa"].strip()
    amendement.auteur = row["Auteur "]
    amendement.matricule = extract_matricule(row["Fiche Sénateur"])
    amendement.date_depot = parse_date(row["Date de dépôt "])
    amendement.sort = row["Sort "]
    amendement.dispositif = clean_html(row["Dispositif "])
    amendement.objet = clean_html(row["Objet "])
    return amendement, created


class DiscussionDetails(NamedTuple):
    num: int
    position: int
    discussion_commune: Optional[int]
    identique: bool
    parent_num: Optional[int]


def parse_discussion_details(
    uid_map: Dict[str, int], amend: dict, position: int
) -> DiscussionDetails:
    num, rectif = Amendement.parse_num(amend["num"])
    details = DiscussionDetails(
        num=num,
        position=position,
        discussion_commune=(
            int(amend["idDiscussionCommune"])
            if parse_bool(amend["isDiscussionCommune"])
            else None
        ),
        identique=parse_bool(amend["isIdentique"]),
        parent_num=get_parent_num(uid_map, amend),
    )
    return details


FICHE_RE = re.compile(r"^[\w\/_]+(\d{5}[\da-z])\.html$")


def extract_matricule(url: str) -> Optional[str]:
    if url == "":
        return None
    mo = FICHE_RE.match(urlparse(url).path)
    if mo is not None:
        return mo.group(1).upper()
    raise ValueError(f"Could not extract matricule from '{url}'")


def parse_bool(text: str) -> bool:
    if text == "true":
        return True
    if text == "false":
        return False
    raise ValueError


def get_parent_num(uid_map: Dict[str, int], amend: dict) -> Optional[int]:
    if (
        "isSousAmendement" in amend
        and parse_bool(amend["isSousAmendement"])
        and "idAmendementPere" in amend
    ):
        return uid_map[amend["idAmendementPere"]]
    else:
        return None
