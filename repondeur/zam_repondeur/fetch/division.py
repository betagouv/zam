import re

from zam_repondeur.fetch.models import SubDiv


SUBDIV_RE = re.compile(
    r"""^
        (?:
            (
                (art|div)\.\sadd\.
                |
                Article(?:\(s\))?\sadditionnel(?:\(s\))?
            )
            \s
            (?P<pos>(avant|après))
            \s
        )?  # position
        (?:(?:l')?article\s)+
        (?P<num>\d+|1er|premier)
        (?:\s(?P<mult>\w+))?        # bis, ter, etc.
        (?:\s?\(?.*\)?)?            # junk
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

    mo = SUBDIV_RE.match(libelle)
    if mo is not None:
        num = "1" if mo.group("num").lower() in {"1er", "premier"} else mo.group("num")
        return SubDiv("article", num, mo.group("mult") or "", mo.group("pos") or "")

    raise ValueError(f"Could not parse subdivision {libelle!r}")
