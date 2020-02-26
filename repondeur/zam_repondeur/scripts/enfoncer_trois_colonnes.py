"""
Experiment: enfoncer un tableau 3 colonnes dans Zam
"""
import logging
import sys
from argparse import ArgumentParser, Namespace
from datetime import date
from typing import List

import transaction
from pyramid.paster import bootstrap, setup_logging

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

logger = logging.getLogger(__name__)


def main(argv: List[str] = sys.argv) -> None:

    args = parse_args(argv[1:])

    setup_logging(args.config_uri)

    log_level = logging.WARNING
    if args.verbose:
        log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG
    logging.getLogger().setLevel(log_level)
    logging.getLogger("urllib3.connectionpool").setLevel(log_level)

    with bootstrap(args.config_uri, options={"app": "zam_fake"}):
        with transaction.manager:
            texte = create_texte()
            print(texte)
            dossier = create_dossier()
            print(dossier)
            lecture = create_lecture(dossier=dossier, texte=texte)
            print(lecture)
            article = create_article(lecture=lecture)
            print(article)
            amendement = create_amendement(lecture=lecture, article=article)
            print(amendement)
            # create_reponses(lecture)


def parse_args(argv: List[str]) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("config_uri")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")
    return parser.parse_args(argv)


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


def create_dossier() -> Dossier:
    dossier, _ = get_one_or_create(
        Dossier,
        titre="Projet de décret relatif au contrat de projet dans la fonction publique",
        slug="projet-de-decret-relatif-au-contrat-de-projet-dans-la-fonction-publique",
        an_id="dummy",
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


def create_article(lecture: Lecture) -> Article:
    article, _ = get_one_or_create(Article, type="article", num="1", lecture=lecture)
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
