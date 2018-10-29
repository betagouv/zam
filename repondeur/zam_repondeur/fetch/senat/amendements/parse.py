import re
from typing import Dict, Optional, Tuple, cast
from urllib.parse import urlparse

from zam_repondeur.clean import clean_html
from zam_repondeur.fetch.dates import parse_date
from zam_repondeur.fetch.division import _parse_subdiv
from zam_repondeur.models import (
    DBSession,
    Article,
    Amendement,
    Lecture,
    get_one_or_create,
)


def parse_from_csv(row: dict, lecture: Lecture) -> Tuple[Amendement, bool]:
    subdiv = _parse_subdiv(row["Subdivision "])
    article, created = get_one_or_create(
        DBSession,
        Article,
        lecture=lecture,
        type=subdiv.type_,
        num=subdiv.num,
        mult=subdiv.mult,
        pos=subdiv.pos,
    )
    num, rectif = Amendement.parse_num(row["Numéro "])
    amendement, created = get_one_or_create(
        DBSession,
        Amendement,
        create_method="create",
        create_method_kwargs={"article": article},
        lecture=lecture,
        num=num,
    )
    # Why do we still need this line?!
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


def parse_from_json(
    uid_map: Dict[str, Amendement],
    amend: dict,
    position: int,
    lecture: Lecture,
    subdiv: dict,
) -> Amendement:
    subdiv_ = _parse_subdiv(subdiv["libelle_subdivision"])
    article, created = get_one_or_create(
        DBSession,
        Article,
        lecture=lecture,
        type=subdiv_.type_,
        num=subdiv_.num,
        mult=subdiv_.mult,
        pos=subdiv_.pos,
    )
    num, rectif = Amendement.parse_num(amend["num"])
    parent = get_parent(uid_map, amend)
    amendement, created = get_one_or_create(
        DBSession,
        Amendement,
        create_method="create",
        create_method_kwargs={"article": article, "parent": parent},
        lecture=lecture,
        num=num,
    )
    # Why do we still need these two lines?!
    amendement.article = article
    amendement.parent = parent
    amendement.rectif = rectif
    amendement.alinea = amend["libelleAlinea"]
    amendement.auteur = amend["auteur"]
    amendement.matricule = (
        extract_matricule(amend["urlAuteur"])
        if amend["auteur"] != "LE GOUVERNEMENT"
        else None
    )
    amendement.sort = amend.get("sort")
    amendement.position = position
    amendement.identique = parse_bool(amend["isIdentique"])
    amendement.discussion_commune = (
        int(amend["idDiscussionCommune"])
        if parse_bool(amend["isDiscussionCommune"])
        else None
    )
    return cast(Amendement, amendement)


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


def get_parent(uid_map: Dict[str, Amendement], amend: dict) -> Optional[Amendement]:
    if (
        "isSousAmendement" in amend
        and parse_bool(amend["isSousAmendement"])
        and "idAmendementPere" in amend
    ):
        return uid_map[amend["idAmendementPere"]]
    else:
        return None
