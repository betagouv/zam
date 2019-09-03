"""
Add an allowed pattern to the email authentication whitelist
"""
import logging
import sys
from argparse import ArgumentParser, Namespace
from operator import attrgetter
from typing import List, Optional

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
            add_pattern(pattern=args.pattern, comment=args.comment)
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
        "pattern", help=AllowedEmailPattern.pattern.doc  # type: ignore
    )
    parser_add.add_argument(
        "--comment", help=AllowedEmailPattern.comment.doc  # type: ignore
    )

    subparsers.add_parser("list", help="list patterns in email whitelist")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    return args


def add_pattern(pattern: str, comment: Optional[str]) -> None:
    with transaction.manager:
        instance = (
            DBSession.query(AllowedEmailPattern).filter_by(pattern=pattern).first()
        )
        if instance is not None:
            print(f"Pattern {pattern} already exists", file=sys.stderr)
            sys.exit(1)
        AllowedEmailPattern.create(pattern=pattern, comment=comment)


def list_patterns() -> None:
    for p in sorted(DBSession.query(AllowedEmailPattern), key=attrgetter("created_at")):
        print(p.created_at.isoformat(" ")[:19], p.pattern, p.comment or "", sep="\t")
