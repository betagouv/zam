"""
Experiment: enfoncer un tableau 1/2/3 colonnes dans Zam

Usage:

    visam_colonnes development.ini --input ~/path/to.csv --colonnes=2
"""
import csv
import logging
import re
import sys
from argparse import ArgumentParser, FileType, Namespace
from collections import defaultdict
from datetime import date
from typing import Dict, List, NamedTuple, Optional, TextIO, Tuple

import transaction
from pyramid.paster import bootstrap
from pyramid.paster import setup_logging as _setup_logging

from zam_repondeur.models import (
    Amendement,
    Article,
    Chambre,
    Dossier,
    Lecture,
    Phase,
    Texte,
    TypeTexte,
    get_one_or_create,
)
from zam_repondeur.models.division import SubDiv
from zam_repondeur.models.events.lecture import LectureCreee
from zam_repondeur.services.fetch.division import parse_subdiv
from zam_repondeur.services.import_export.csv import guess_csv_delimiter
from zam_repondeur.slugs import slugify

logger = logging.getLogger(__name__)


def main(argv: List[str] = sys.argv) -> None:
    args = parse_args(argv[1:])
    setup_logging(args)

    dossier, articles, amendements = extract_data_from_csv_file(args.input)

    with bootstrap(args.config_uri, options={"app": "visam_trois_colonnes"}):
        with transaction.manager:
            load_data(dossier, articles, amendements, colonnes=args.colonnes)


NumAmendement = str


class AmendementData(NamedTuple):
    num_article: SubDiv
    num_amendement: NumAmendement
    auteur: str
    groupe: str
    corps: str
    expose: str
    comments: str
    avis: Optional[str]
    reponse: str


def extract_data_from_csv_file(
    input_file: TextIO,
) -> Tuple[dict, dict, List[AmendementData]]:
    articles: Dict[SubDiv, List[str]] = defaultdict(list)
    amendements: Dict[Tuple[NumAmendement, int], AmendementData] = {}

    reader = csv.DictReader(
        input_file,
        fieldnames=["numero_article", "texte_article", "amendements", "avis"],
        delimiter=guess_csv_delimiter(input_file),
    )

    # La première ligne contient le titre du dossier
    first_line = next(reader)
    dossier = {"titre": first_line["texte_article"]}

    # La deuxième ligne est vide
    next(reader)

    # La troisième ligne contient les en-têtes de colonnes
    next(reader)

    num_amendement = None
    auteur = ""
    groupe = ""
    comments = ""

    # Les lignes non vides contiennent les articles et amendements associés
    non_empty_lines = (line for line in reader if line != ("", "", "", ""))
    for line in non_empty_lines:
        numero_article = parse_subdiv(line["numero_article"])
        if numero_article.mult == "bis":  # bis
            numero_article = numero_article._replace(mult="", pos="après")

        # On accumule le texte de l'article, qui peut être réparti sur plusieurs lignes
        texte_article = line["texte_article"].strip()
        if texte_article or numero_article not in articles:
            articles[numero_article].append(texte_article)

        # Un amendement est réparti sur 2 ou 3 lignes
        texte_amendement = line["amendements"]

        # Début de la séquence : numéro d'amendement et avis
        if num_amendement is None:
            mo = re.match(
                (
                    r"Amendement "
                    r"((employeurs\sterritoriaux|Gouvernement|[A-Z-]{2,})"
                    r"(\s\d+)?)"
                ),
                texte_amendement,
            )
            if mo is not None:
                # Numéro d'amendement
                num_amendement = mo.group(1)
                copie_amendement = 1
                while (num_amendement, copie_amendement) in amendements:
                    copie_amendement += 1

                # Extraction de l'auteur
                if mo.group(2) == "Gouvernement":
                    auteur = "LE GOUVERNEMENT"
                else:
                    groupe = mo.group(2)

                # Extraction de l'avis
                reponse = line["avis"]
                avis = parse_avis(reponse.split("\n", 1)[0].strip())
                reponse = reponse.replace("\n", "<br>")

        # Suite de la séquence
        elif texte_amendement:
            # Commentaire (ignoré pour l'instant)
            if re.match(
                r"\s*(Identique|Similair?e|A traiter) .*",
                texte_amendement,
                flags=re.IGNORECASE,
            ):
                comments = texte_amendement
            else:
                mo = re.match(
                    r"\s*Texte de l’amendement\s?:?(.*?)Exposé des motifs\s?:(.*)",
                    texte_amendement,
                    flags=re.MULTILINE | re.DOTALL,
                )
                if mo is not None:
                    corps = mo.group(1).strip().replace("\n", "<br><br>")
                    expose = mo.group(2).strip().replace("\n", "<br><br>")
                else:
                    corps = texte_amendement
                    expose = ""

                # Les amendements modifiant plusieurs articles sont dupliqués
                numero_avec_mult = num_amendement
                if copie_amendement > 1:
                    numero_avec_mult += (
                        " " + Amendement._RECTIF_TO_SUFFIX[copie_amendement]
                    )
                amendements[(num_amendement, copie_amendement)] = AmendementData(
                    num_article=numero_article,
                    num_amendement=numero_avec_mult,
                    corps=corps,
                    expose=expose,
                    auteur=auteur,
                    groupe=groupe,
                    avis=avis,
                    reponse=reponse,
                    comments=comments,
                )
                num_amendement = None  # terminé
                auteur = ""  # terminé
                groupe = ""  # terminé
                comments = ""  # terminé

    return dossier, articles, list(amendements.values())


def parse_avis(line: str) -> Optional[str]:
    if line in {"Favorable", "Avis favorable"}:
        return "Favorable"
    if line in {"Défavorable", "Avis défavorable"}:
        return "Défavorable"
    if line in {
        "Retrait - à défaut défavorable",
        "Retrait car satisfait - à défaut avis défavorable",
        "Retrait car staisfait - à défaut avis défavorable",
        "Retrait car satisfait (à défaut avis défavorable)",
        "Retrait au bénéfice d'explication - à défaut avis défavorable",
        "Retrait au bénéfice d'explication ou à défaut avis défavorable",
    }:
        return "Retrait sinon rejet"
    if line in {
        "Avis favorable sous réserve d'un sous-amendement",
        "Réponse de la DGCL : Favorable sous réserve de l'examen du CE",
    }:
        return "Favorable sous réserve de"
    if line == "Position DGCL :  sagesse":
        return "Sagesse"
    if line == "":
        return None
    raise ValueError(f"Cannot parse {line!r}")


def load_data(
    dossier: dict,
    articles: Dict[SubDiv, List[str]],
    amendements: List[AmendementData],
    colonnes: int,
) -> None:
    texte = create_texte()
    dossier = create_dossier(titre=dossier["titre"])
    lecture = create_lecture(dossier=dossier, texte=texte)
    articles_by_num = {
        numero: create_article(lecture=lecture, numero=numero, alineas=alineas)
        for numero, alineas in articles.items()
    }
    if colonnes >= 2:
        for position, amendement in enumerate(amendements, 1):
            reponse = {
                "avis": amendement.avis,
                "reponse": amendement.reponse,
                "comments": amendement.comments,
            }
            create_amendement(
                lecture=lecture,
                article=articles_by_num[amendement.num_article],
                num=amendement.num_amendement,
                corps=amendement.corps,
                expose=amendement.expose,
                auteur=amendement.auteur,
                groupe=amendement.groupe,
                position=position,
                **reponse if colonnes == 3 else {},
            )


def create_texte() -> Texte:
    texte, _ = get_one_or_create(
        Texte,
        type_=TypeTexte.PROJET,
        chambre=Chambre.CCFP,
        numero=1,
        create_kwargs={"date_depot": date.today()},
    )
    return texte


def create_dossier(titre: str) -> Dossier:
    dossier, _ = get_one_or_create(
        Dossier, slug=slugify(titre), create_kwargs={"titre": titre, "an_id": "dummy"}
    )
    return dossier


def create_lecture(texte: Texte, dossier: Dossier) -> Lecture:
    organe = "Assemblée plénière"
    lecture, _ = get_one_or_create(
        Lecture,
        dossier=dossier,
        texte=texte,
        phase=Phase.PREMIERE_LECTURE,
        organe=organe,
        titre=f"Première lecture – {organe}",
    )
    LectureCreee.create(lecture=lecture, user=None)
    return lecture


def create_article(lecture: Lecture, numero: SubDiv, alineas: list) -> Article:
    if alineas[0].startswith("Article "):
        alineas.pop(0)
    content = {str(i).zfill(3): alinea for i, alinea in enumerate(alineas, start=1)}
    article, _ = get_one_or_create(
        Article,
        type=numero.type_,
        num=numero.num,
        mult=numero.mult,
        pos=numero.pos,
        lecture=lecture,
        content=content,
    )
    return article


def create_amendement(
    lecture: Lecture,
    article: Article,
    num: NumAmendement,
    corps: str,
    expose: str,
    auteur: str,
    groupe: str,
    position: int,
    avis: Optional[str] = None,
    reponse: Optional[str] = None,
    comments: Optional[str] = None,
) -> Amendement:
    amendement, _ = get_one_or_create(
        Amendement,
        lecture=lecture,
        article=article,
        num=num,
        create_kwargs={
            "corps": corps,
            "expose": expose,
            "auteur": auteur,
            "groupe": groupe,
            "avis": avis,
            "reponse": reponse,
            "comments": comments,
            "position": position,
        },
    )
    return amendement


def parse_args(argv: List[str]) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("config_uri")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-i", "--input", type=FileType("r"), required=True)
    parser.add_argument("-c", "--colonnes", type=int, default=3, choices=[1, 2, 3])
    return parser.parse_args(argv)


def setup_logging(args: Namespace) -> None:
    _setup_logging(args.config_uri)

    log_level = logging.WARNING
    if args.verbose:
        log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG
    logging.getLogger().setLevel(log_level)
    logging.getLogger("urllib3.connectionpool").setLevel(log_level)
