import logging
import re
from typing import NamedTuple


logger = logging.getLogger(__name__)


class SubDiv(NamedTuple):
    type_: str
    num: str
    mult: str
    pos: str


SUBDIV_RE = re.compile(
    r"""^
        (?:
            (
                (art|div)\.\sadd\.
                |
                Article(?:\(s\))?\sadditionnel(?:\(s\))?
            )?
            \s?
            (?P<pos>((?i)avant|après|apres))
            \s
        )?  # position
        \s?
        (?:(?:l')?article(?:s)?\s)+
        (?P<num>liminaire|1er|premier|\d+)
        (?:\s(?P<mult>\w+(\s[A-Z]$)?))?  # bis, ter, bis C, etc.
        (?:\s?\(?.*\)?)?  # junk
        $
    """,
    (re.VERBOSE | re.IGNORECASE),
)


TITRE_RE = re.compile(r"Titre (?P<num>\w+)(?: .*)?", re.IGNORECASE)


def _parse_subdiv(libelle: str) -> SubDiv:
    if libelle == "":
        return SubDiv("", "", "", "")

    if libelle == "Intitulé du projet de loi":
        return SubDiv("titre", "", "", "")

    if libelle == "Motions":
        return SubDiv("motion", "", "", "")

    mo = TITRE_RE.match(libelle)
    if mo is not None:
        return SubDiv("section", mo.group("num"), "", "")

    if libelle.lower().startswith("annexe"):
        start = len("annexe")
        return SubDiv("annexe", libelle[start:].strip(), "", "")

    if libelle.startswith("Chapitre "):
        start = len("Chapitre ")
        return SubDiv("chapitre", libelle[start:], "", "")

    if libelle.startswith("Section "):
        start = len("Section ")
        return SubDiv("section", libelle[start:], "", "")

    if libelle.startswith("Soussection "):
        start = len("Soussection ")
        return SubDiv("sous-section", libelle[start:], "", "")

    if " à " in libelle:
        libelle = libelle.split(" à ")[0]
        logger.warning("Amendement targets a range of subdivs, keeping only first")

    mo = SUBDIV_RE.match(libelle)
    if mo is not None:
        if mo.group("num").lower() == "liminaire":
            num = "0"
        elif mo.group("num").lower() in {"1er", "premier"}:
            num = "1"
        else:
            num = mo.group("num")
        if mo.group("pos"):
            pos = mo.group("pos").lower()
            if pos == "apres":
                pos = "après"
        else:
            pos = ""
        return SubDiv("article", num, mo.group("mult") or "", pos)

    raise ValueError(f"Could not parse subdivision {libelle!r}")
