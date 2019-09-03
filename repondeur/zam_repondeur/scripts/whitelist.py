"""
Add an allowed pattern to the email authentication whitelist
"""
import logging
import sys
from argparse import ArgumentParser, Namespace
from typing import List

import transaction
from pyramid.paster import bootstrap, setup_logging

from zam_repondeur.models import DBSession
from zam_repondeur.models.users import AllowedEmailPattern

logger = logging.getLogger(__name__)


def main(argv: List[str] = sys.argv) -> None:

    args = parse_args(argv[1:])

    setup_logging(args.config_uri)

    logging.getLogger().setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

    with bootstrap(args.config_uri, options={"app": "zam_load_data"}):
        if args.command == "add":
            add_pattern(args.pattern)
        elif args.command == "list":
            list_patterns()
        else:
            sys.exit(1)


def parse_args(argv: List[str]) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("config_uri")

    subparsers = parser.add_subparsers(dest="command", metavar="command")

    parser_add = subparsers.add_parser("add", help="add pattern to the email whitelist")
    parser_add.add_argument(
        "pattern", help="a glob-style pattern matching allowed addresses"
    )

    subparsers.add_parser("list", help="list patterns in email whitelist")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    return args


def add_pattern(pattern: str) -> None:
    with transaction.manager:
        AllowedEmailPattern.create(pattern=pattern)


def list_patterns() -> None:
    for pattern in sorted(p.pattern for p in DBSession.query(AllowedEmailPattern)):
        print(pattern)
