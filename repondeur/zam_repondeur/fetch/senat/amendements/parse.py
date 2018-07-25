import re
from datetime import date, datetime
from typing import Optional
from urllib.parse import urlparse

from zam_repondeur.clean import clean_html
from zam_repondeur.fetch.division import _parse_subdiv
from zam_repondeur.fetch.models import Amendement


def parse_from_csv(row: dict, session: str, num_texte: int, organe: str) -> Amendement:
    num, rectif = Amendement.parse_num(row["Numéro "])
    subdiv_type, subdiv_num, subdiv_mult, subdiv_pos = _parse_subdiv(
        row["Subdivision "]
    )
    return Amendement(  # type: ignore
        chambre="senat",
        session=session,
        num_texte=num_texte,
        organe=organe,
        num=num,
        rectif=rectif,
        subdiv_type=subdiv_type,
        subdiv_num=subdiv_num,
        subdiv_mult=subdiv_mult,
        subdiv_pos=subdiv_pos,
        alinea=row["Alinéa"].strip(),
        auteur=row["Auteur "],
        matricule=extract_matricule(row["Fiche Sénateur"]),
        date_depot=parse_date(row["Date de dépôt "]),
        sort=row["Sort "],
        dispositif=clean_html(row["Dispositif "]),
        objet=clean_html(row["Objet "]),
    )


def parse_from_json(
    amends_by_ids: dict,
    amend: dict,
    position: int,
    session: str,
    num_texte: int,
    organe: str,
    subdiv: dict,
) -> Amendement:
    num, rectif = Amendement.parse_num(amend["num"])
    subdiv_type, subdiv_num, subdiv_mult, subdiv_pos = _parse_subdiv(
        subdiv["libelle_subdivision"]
    )
    parent_num, parent_rectif = Amendement.parse_num(
        get_parent_raw_num(amends_by_ids, amend)
    )
    return Amendement(  # type: ignore
        chambre="senat",
        session=session,
        num_texte=num_texte,
        organe=organe,
        subdiv_type=subdiv_type,
        subdiv_num=subdiv_num,
        subdiv_mult=subdiv_mult,
        subdiv_pos=subdiv_pos,
        num=num,
        rectif=rectif,
        alinea=amend["libelleAlinea"],
        auteur=amend["auteur"],
        matricule=(
            extract_matricule(amend["urlAuteur"])
            if amend["auteur"] != "LE GOUVERNEMENT"
            else None
        ),
        sort=amend.get("sort"),
        parent_num=parent_num,
        parent_rectif=parent_rectif,
        position=position,
        identique=parse_bool(amend["isIdentique"]),
        discussion_commune=(
            int(amend["idDiscussionCommune"])
            if parse_bool(amend["isDiscussionCommune"])
            else None
        ),
    )


FICHE_RE = re.compile(r"^[\w\/_]+(\d{5}[\da-z])\.html$")


def extract_matricule(url: str) -> Optional[str]:
    if url == "":
        return None
    mo = FICHE_RE.match(urlparse(url).path)
    if mo is not None:
        return mo.group(1).upper()
    raise ValueError(f"Could not extract matricule from '{url}'")


def parse_date(text: str) -> Optional[date]:
    if text == "":
        return None
    return datetime.strptime(text, "%Y-%m-%d").date()


def parse_bool(text: str) -> bool:
    if text == "true":
        return True
    if text == "false":
        return False
    raise ValueError


def get_parent_raw_num(amends_by_ids: dict, amend: dict) -> str:
    if (
        "isSousAmendement" in amend
        and parse_bool(amend["isSousAmendement"])
        and "idAmendementPere" in amend
    ):
        num: str = amends_by_ids[amend["idAmendementPere"]]["num"]
        return num
    return ""
