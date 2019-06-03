"""
Parser for subdivisions (article, chapitre...)

This implementation uses the parsy library to allow some
modularity and easier maintenance than a big regex...

https://parsy.readthedocs.io/en/latest/overview.html

"""
import logging
from typing import Any, List, Optional

from parsy import ParseError, regex, seq, string, string_from, whitespace

from zam_repondeur.models.division import ADJECTIFS_MULTIPLICATIFS, SubDiv
from zam_repondeur.models.texte import Texte

logger = logging.getLogger(__name__)


def case_insensitive_string(expected_string: str) -> Any:
    return string(expected_string, transform=lambda s: s.lower())


def case_insensitive_string_from(*expected_strings: str) -> Any:
    return string_from(*expected_strings, transform=lambda s: s.lower())


# Numéro

CHIFFRES_ARABES = case_insensitive_string_from("1e", "1er", "1ère").result("1") | regex(
    r"\d+"
)

CHIFFRES_ROMAINS = case_insensitive_string("Ier") | regex(r"[IVXLCDM]+")

LETTRES = regex(r"[A-Z]+")

NUMERO = (
    string("liminaire").result("0")
    | case_insensitive_string_from("premier", "unique").result("1")
    | string("PRÉLIMINAIRE")
    | CHIFFRES_ARABES
    | CHIFFRES_ROMAINS
    | LETTRES
)

MULTIPLICATIF = string_from(*ADJECTIFS_MULTIPLICATIFS)

ADDITIONNEL = regex(r"[A-Z]+")  # alias "andouillette" (AAAAA)

MULT_ADD = (
    seq(MULTIPLICATIF << whitespace.optional(), ADDITIONNEL).map(" ".join)
    | MULTIPLICATIF
    | ADDITIONNEL
)


# Divisions uniques

INTITULE = (
    (
        case_insensitive_string("Intitulé")
        >> whitespace
        >> case_insensitive_string_from("de la", "de  la", "du")
        >> whitespace
    ).optional()
    >> case_insensitive_string_from(
        "proposition de loi", "projet de loi", "texte"
    ).result("titre")
    << regex(".*")
)

MOTION = string("Motions").result("motion")

DIVISION_UNIQUE = (INTITULE | MOTION).map(lambda type_: SubDiv.create(type_=type_))


# Divisions numérotées

CHAPITRE = (case_insensitive_string("Chapitre") << whitespace).result("chapitre")

TITRE = (case_insensitive_string("Titre") << whitespace).result("section")

SECTION = (case_insensitive_string("Section") << whitespace).result("section")

SOUS_SECTION = (
    case_insensitive_string_from("Soussection", "Sous-section") << whitespace
).result("sous-section")

BLA_BLA = (
    regex(r"\s*:\s+.+")  # xxx : bla bla
    | regex(r"\s\s.+")  # xxx  bla bla
    | regex(r"\s*-\s+.+")  # xxx - Bla bla
    | regex(r"\s*\(.*\)?")  # xxx (bla bla)
    | regex(r"\s*\[.*\]")  # xxx [bla bla]
    | regex(r"\s*.*")  # xxx bla bla
    | whitespace
)

DIVISION_NUMEROTEE = (
    seq(
        (CHAPITRE | TITRE | SECTION | SOUS_SECTION).tag("type_"),
        NUMERO.tag("num"),
        (whitespace >> MULTIPLICATIF).optional().tag("mult"),
    )
    .combine_dict(SubDiv.create)
    .skip(BLA_BLA.optional())
)


# Article(s)


def check_all_equal(pos_list: List[str]) -> str:
    if len(set(pos_list)) != 1:
        raise RuntimeError(f"Inconsistent data ({pos_list!r})")
    return pos_list[0]


ARTICLE = (
    (case_insensitive_string_from("Art.", "Article", "Articles") << whitespace)
    .optional()
    .result("article")
)

AVANT_APRES = (
    (
        string_from(
            "art. add.",
            "div. add.",
            "Article additionnel",
            "Articles additionnels",
            "Article(s) additionnel(s)",
        )
        << whitespace
    ).optional()
    >> (
        case_insensitive_string("après").result("après")
        | case_insensitive_string("apres").result("après")
        | case_insensitive_string("avant").result("avant")
    )
    << whitespace
).at_least(1).map(check_all_equal) << case_insensitive_string("l'").optional()


ARTICLE_UNIQUE = (
    seq(
        ARTICLE.tag("type_"),
        (case_insensitive_string("article") << whitespace).optional().tag(None),
        NUMERO.tag("num"),
        (whitespace.optional() >> MULT_ADD << whitespace.optional())
        .optional()
        .tag("mult"),
    )
    .combine_dict(SubDiv.create)
    .skip(BLA_BLA.optional())
)


ART_ADD_TITRE = seq(AVANT_APRES.tag("pos"), INTITULE.tag("type_")).combine_dict(
    SubDiv.create
)

ART_ADD_DIVISION = (
    seq(
        AVANT_APRES.tag("pos"),
        (CHAPITRE | TITRE).tag("type_"),
        NUMERO.tag("num"),
        (whitespace >> MULTIPLICATIF).optional().tag("mult"),
    )
    .combine_dict(SubDiv.create)
    .skip(BLA_BLA.optional())
)

ART_ADD_ARTICLE = (
    seq(
        AVANT_APRES.tag("pos"),
        ARTICLE.tag("type_"),
        NUMERO.tag("num"),
        (whitespace >> MULT_ADD).optional().tag("mult"),
    )
    .combine_dict(SubDiv.create)
    .skip(BLA_BLA.optional())
)

ARTICLE_ADDITIONNEL = ART_ADD_TITRE | ART_ADD_DIVISION | ART_ADD_ARTICLE


INTERVALLE = seq(
    ARTICLE.tag("type_"),
    NUMERO.tag("num"),
    (whitespace >> MULT_ADD).optional().tag("mult"),
    seq(
        whitespace,
        string("\xe0"),
        whitespace,
        NUMERO,
        (whitespace >> MULT_ADD).optional(),
    ).tag(None),
).combine_dict(SubDiv.create)


ANNEXE = seq(
    case_insensitive_string("annexe").result("annexe").tag("type_"),
    (whitespace >> NUMERO).optional().tag("num"),
).combine_dict(SubDiv.create)


EMPTY = string("").result(SubDiv.create(type_=""))


# Main parser

DIVISION = (
    ANNEXE
    | DIVISION_UNIQUE
    | DIVISION_NUMEROTEE
    | INTERVALLE  # must remain before ARTICLE_* parsing.
    | ARTICLE_ADDITIONNEL
    | ARTICLE_UNIQUE
    | EMPTY
)


def parse_subdiv(libelle: str, texte: Optional[Texte] = None) -> SubDiv:
    try:
        subdiv: SubDiv = DIVISION.parse(libelle)
        return subdiv
    except (ParseError, RuntimeError):
        logger.exception(f"Could not parse subdivision {libelle!r}")
        return SubDiv("erreur", "", "", "")
