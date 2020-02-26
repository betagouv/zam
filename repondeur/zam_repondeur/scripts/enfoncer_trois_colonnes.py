"""
Experiment: enfoncer un tableau 3 colonnes dans Zam
"""
import logging
import sys
from argparse import ArgumentParser, Namespace
from datetime import date
from typing import List, Optional

import transaction
from pyramid.paster import bootstrap, setup_logging

from zam_repondeur.models import Amendement, Chambre, DBSession, Lecture, Texte

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
            dossier = create_dossier(texte)
            lecture = create_lecture(dossier=dossier, texte=texte)
            create_amendements(lecture)
            create_reponses(lecture)


def parse_args(argv: List[str]) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("config_uri")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")
    return parser.parse_args(argv)
