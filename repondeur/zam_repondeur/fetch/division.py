"""
Parser for subdivisions (article, chapitre...)

This implementation uses the parsy library to allow some
modularity and easier maintenance than a big regex...

https://parsy.readthedocs.io/en/latest/overview.html

"""
import re
import logging
from typing import Any, List, Optional

from parsy import ParseError, regex, seq, string, string_from, whitespace

from zam_repondeur.models.division import ADJECTIFS_MULTIPLICATIFS, SubDiv
from zam_repondeur.models.texte import Texte

logger = logging.getLogger(__name__)

VERY_BIG_NUMBER = 999_999_999


def case_insensitive_string(expected_string: str) -> Any:
    return string(expected_string, transform=lambda s: s.lower())


def case_insensitive_string_from(*expected_strings: str) -> Any:
    return string_from(*expected_strings, transform=lambda s: s.lower())


# Numéro

CHIFFRES_ARABES = case_insensitive_string("1er").result("1") | regex(r"\d+")

CHIFFRES_ROMAINS = case_insensitive_string("Ier") | regex(r"[IVXLCDM]+")

LETTRES = regex(r"[A-Z]+")

NUMERO = (
    string("liminaire").result("0")
    | case_insensitive_string("premier").result("1")
    | CHIFFRES_ARABES
    | CHIFFRES_ROMAINS
    | LETTRES
)

MULTIPLICATIF = string_from(*ADJECTIFS_MULTIPLICATIFS)

ADDITIONNEL = regex(r"[A-Z]+")  # alias "andouillette" (AAAAA)

MULT_ADD = (
    seq(MULTIPLICATIF.skip(whitespace), ADDITIONNEL).map(" ".join)
    | MULTIPLICATIF
    | ADDITIONNEL
)


# Divisions uniques

INTITULE = string_from(
    "Intitulé de la proposition de loi",
    "Intitulé du projet de loi",
    "Intitulé du projet de loi constitutionnelle",
).result("titre")

MOTION = string("Motions").result("motion")

DIVISION_UNIQUE = (INTITULE | MOTION).map(lambda type_: SubDiv.create(type_=type_))


# Divisions numérotées

CHAPITRE = case_insensitive_string("Chapitre").result("chapitre")

TITRE = case_insensitive_string("Titre").result("section")

SECTION = case_insensitive_string("Section").result("section")

SOUS_SECTION = case_insensitive_string_from("Soussection", "Sous-section").result(
    "sous-section"
)

BLA_BLA = (
    regex(r"\s+:\s+.+")  # xxx : bla bla
    | regex(r"\s+-\s+.+")  # xxx - Bla bla
    | regex(r"\s+\(.*\)")  # xxx (bla bla)
)

DIVISION_NUMEROTEE = (
    seq(
        (CHAPITRE | TITRE | SECTION | SOUS_SECTION).tag("type_"),
        (whitespace >> NUMERO).tag("num"),
        (whitespace >> MULT_ADD).optional().tag("mult"),
    )
    .combine_dict(SubDiv.create)
    .skip(BLA_BLA.optional())
)


# Article(s)


def check_all_equal(pos_list: List[str]) -> str:
    assert len(set(pos_list)) == 1, pos_list
    return pos_list[0]


ARTICLE = case_insensitive_string("Article").result("article")
ARTICLES = case_insensitive_string("Articles").result("article")

AVANT_APRES = (
    (
        string_from(
            "art. add.", "div. add.", "Article additionnel", "Article(s) additionnel(s)"
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


STATUT_NAVETTE = seq(
    whitespace.optional(),
    string("("),
    case_insensitive_string_from("nouveau", "précédemment examiné", "supprimé"),
    string(")"),
)


ARTICLE_UNIQUE = (
    seq(
        ARTICLE.tag("type_"),
        (whitespace >> case_insensitive_string("article")).optional().tag(None),
        (whitespace >> NUMERO).tag("num"),
        (whitespace >> MULT_ADD << whitespace.optional()).optional().tag("mult"),
    )
    .combine_dict(SubDiv.create)
    .skip(STATUT_NAVETTE.optional())
    .skip(BLA_BLA.optional())
)


ARTICLE_ADDITIONNEL = (
    seq(
        AVANT_APRES.tag("pos"),
        (ARTICLE | CHAPITRE | TITRE).tag("type_"),
        (whitespace >> NUMERO).tag("num"),
        (whitespace >> MULT_ADD).optional().tag("mult"),
    )
    .combine_dict(SubDiv.create)
    .skip(STATUT_NAVETTE.optional())
    .skip(BLA_BLA.optional())
) | seq(AVANT_APRES.tag("pos"), INTITULE.tag("type_")).combine_dict(SubDiv.create)


INTERVALLE = seq(
    (ARTICLES | ARTICLE).tag("type_"),
    (whitespace >> NUMERO).tag("num"),
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
    DIVISION_UNIQUE
    | DIVISION_NUMEROTEE
    | INTERVALLE  # must remain before ARTICLE_* parsing.
    | ARTICLE_UNIQUE
    | ARTICLE_ADDITIONNEL
    | ANNEXE
    | EMPTY
)


def parse_subdiv(libelle: str, texte: Optional[Texte] = None) -> SubDiv:

    input_string = libelle

    # Case-insensitively replace the litteral title
    if texte is not None and texte.titre_long is not None:
        title_re = re.compile(re.escape(texte.titre_long.lower()), re.I)
        input_string = title_re.sub("Intitulé du projet de loi", input_string)

    try:
        subdiv: SubDiv = DIVISION.parse(input_string)
        return subdiv
    except ParseError:
        logger.warning(f"Could not parse subdivision {libelle!r}")
        return SubDiv("erreur", str(VERY_BIG_NUMBER), "", "")
