import logging
import sys
from argparse import ArgumentParser, Namespace
from typing import List

from pyramid.paster import bootstrap, setup_logging

logger = logging.getLogger(__name__)


def main(argv: List[str] = sys.argv) -> None:

    args = parse_args(argv[1:])

    setup_logging(args.config_uri)

    logging.getLogger().setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

    with bootstrap(args.config_uri, options={"app": "zam_clear_data"}):
        from zam_repondeur.services.amendements import (
            repository as repository_amendements,
        )
        from zam_repondeur.services.data import repository as repository_data
        from zam_repondeur.services.progress import repository as repository_progress
        from zam_repondeur.services.users import repository as repository_users

        repository_amendements.clear_data()
        repository_data.clear_data()
        repository_progress.clear_data()
        repository_users.clear_data()


def parse_args(argv: List[str]) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("config_uri")
    return parser.parse_args(argv)
