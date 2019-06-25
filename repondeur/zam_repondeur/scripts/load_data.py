import logging
import sys
from argparse import ArgumentParser, Namespace
from typing import List

from pyramid.paster import get_appsettings, setup_logging

from zam_repondeur import BASE_SETTINGS
from zam_repondeur.data import init_repository, repository


logger = logging.getLogger(__name__)


def main(argv: List[str] = sys.argv) -> None:

    args = parse_args(argv[1:])

    setup_logging(args.config_uri)

    logging.getLogger().setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

    settings = get_appsettings(args.config_uri)
    settings = {**BASE_SETTINGS, **settings}

    init_repository(settings)
    repository.load_data()


def parse_args(argv: List[str]) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("config_uri")
    return parser.parse_args(argv)
