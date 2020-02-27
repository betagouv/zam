"""
Experiment: enfoncer un tableau 3 colonnes dans Zam

Usage:

    visam_trois_colonnes development.ini --input ~/path/to.csv
"""
import csv
import logging
import sys
from argparse import ArgumentParser, FileType, Namespace
from collections import defaultdict
from datetime import date
from typing import Dict, List, TextIO, Tuple

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
from zam_repondeur.services.import_export.csv import guess_csv_delimiter
from zam_repondeur.slugs import slugify

logger = logging.getLogger(__name__)


def main(argv: List[str] = sys.argv) -> None:
    args = parse_args(argv[1:])
    setup_logging(args)

    dossier, articles = extract_data_from_csv_file(args.input)

    with bootstrap(args.config_uri, options={"app": "visam_trois_colonnes"}):
        with transaction.manager:
            load_data(dossier, articles)


def extract_data_from_csv_file(input_file: TextIO) -> Tuple[dict, dict]:
    delimiter = guess_csv_delimiter(input_file)
    dossier = {}
    articles: Dict[str, list] = defaultdict(list)
    for i, line in enumerate(
        csv.DictReader(
            input_file,
            fieldnames=["numero", "texte", "amendements", "position"],
            delimiter=delimiter,
        )
    ):
        if i == 0:
            dossier["titre"] = line["texte"]
        numero = line["numero"]
        if numero in ("", "N° Article"):
            # TODO: deal with amendements applied to the whole text.
            continue

        texte = line["texte"].strip()
        if texte:
            articles[numero].append(texte)

    return dossier, articles


def load_data(dossier: dict, articles: dict) -> None:
    texte = create_texte()
    print(texte)
    dossier = create_dossier(titre=dossier["titre"])
    print(dossier)
    lecture = create_lecture(dossier=dossier, texte=texte)
    print(lecture)
    for numero, alineas in articles.items():
        article = create_article(lecture=lecture, numero=numero, alineas=alineas)
    print(article)
    # amendement = create_amendement(lecture=lecture, article=article)
    # print(amendement)
    # create_reponses(lecture)


def create_texte() -> Texte:
    texte, _ = get_one_or_create(
        Texte,
        type_=TypeTexte.PROJET,
        chambre=Chambre.AN,  # TODO: CCFP et ...
        legislature=15,
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
    lecture, _ = get_one_or_create(
        Lecture,
        dossier=dossier,
        texte=texte,
        phase=Phase.PREMIERE_LECTURE,
        organe="dummy",  # TODO: distinguer Assemblée Plénière / Formation Spécialisée
        titre="Première lecture – Assemblée plénière",
    )
    return lecture


def create_article(lecture: Lecture, numero: str, alineas: list) -> Article:
    if alineas[0].startswith("Article "):
        alineas.pop(0)
    content = {str(i).zfill(3): alinea for i, alinea in enumerate(alineas, start=1)}
    article, _ = get_one_or_create(
        Article, type="article", num=numero, lecture=lecture, content=content
    )
    return article


def create_amendement(lecture: Lecture, article: Article) -> Amendement:
    amendement, _ = get_one_or_create(
        Amendement,
        lecture=lecture,
        article=article,
        num="FSU 1",
        create_kwargs={
            "corps": "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Debitis vel at laboriosam officiis quibusdam cupiditate molestias impedit in totam quas delectus nesciunt animi unde iste, adipisci rem magnam incidunt nam.",  # noqa
            "expose": "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Consectetur aspernatur illum perferendis labore dolor, qui. Laudantium velit culpa distinctio, dignissimos fuga possimus eaque eveniet ullam voluptatum doloremque doloribus architecto mollitia.",  # noqa
        },
    )
    return amendement


def parse_args(argv: List[str]) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("config_uri")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-i", "--input", type=FileType("r"), required=True)
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
