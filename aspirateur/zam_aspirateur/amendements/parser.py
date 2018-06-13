import re
from datetime import date, datetime
from typing import Optional, Tuple
from urllib.parse import urlparse

from ..clean import clean_html

from .models import Amendement


def parse_from_csv(row: dict, session: str, num_texte: str) -> Amendement:
    subdiv_type, subdiv_num, subdiv_mult, subdiv_pos = _parse_subdiv(
        row["Subdivision "]
    )
    return Amendement(  # type: ignore
        chambre="senat",
        session=session,
        num_texte=num_texte,
        num=row["Numéro "],
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


def parse_from_json(
    amend: dict, position: int, session: str, num_texte: str, subdiv: dict
) -> Amendement:
    subdiv_type, subdiv_num, subdiv_mult, subdiv_pos = _parse_subdiv(
        subdiv["libelle_subdivision"]
    )
    return Amendement(  # type: ignore
        chambre="senat",
        session=session,
        num_texte=num_texte,
        subdiv_type=subdiv_type,
        subdiv_num=subdiv_num,
        subdiv_mult=subdiv_mult,
        subdiv_pos=subdiv_pos,
        num=amend["num"],
        alinea=amend["libelleAlinea"],
        auteur=amend["auteur"],
        matricule=(
            extract_matricule(amend["urlAuteur"])
            if amend["auteur"] != "LE GOUVERNEMENT"
            else None
        ),
        sort=amend["sort"],
        position=position,
        identique=parse_bool(amend["isIdentique"]),
        discussion_commune=(
            amend["idDiscussionCommune"]
            if parse_bool(amend["isDiscussionCommune"])
            else None
        ),
    )


def parse_bool(text: str) -> bool:
    if text == "true":
        return True
    if text == "false":
        return False
    raise ValueError


SUBDIV_RE = re.compile(
    r"""^
        (?:art\.\sadd\.\s(?P<pos>(avant|après))\s)?  # position
        Article\s
        (?P<num>\d+|1er)
        (?:\s(?P<mult>\w+))?        # bis, ter, etc.
        (?:\s.*)?                   # junk
        $
    """,
    re.VERBOSE,
)


def _parse_subdiv(libelle: str) -> Tuple[str, str, str, str]:
    if libelle == "":
        return ("", "", "", "")
    if libelle.startswith("ANNEXE "):
        start = len("ANNEXE ")
        return ("annexe", libelle[start:], "", "")
    if libelle.startswith("Chapitre "):
        start = len("Chapitre ")
        return ("chapitre", libelle[start:], "", "")
    mo = SUBDIV_RE.match(libelle)
    if mo is None:
        raise ValueError(f"Could not parse subdivision {libelle!r}")
    num = "1" if mo.group("num") == "1er" else mo.group("num")
    return "article", num, mo.group("mult") or "", mo.group("pos") or ""
