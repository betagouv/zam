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
from zam_repondeur.models.events.whitelist import WhitelistAdd, WhitelistRemove
from zam_repondeur.models.users import AllowedEmailPattern, User

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
        elif args.command == "remove":
            remove_pattern(pattern=args.pattern)
        elif args.command == "check":
            check_email(email=args.email)
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

    parser_remove = subparsers.add_parser(
        "remove", help="remove pattern from the email whitelist"
    )
    parser_remove.add_argument(
        "pattern", help=AllowedEmailPattern.pattern.doc  # type: ignore
    )

    parser_check = subparsers.add_parser(
        "check", help="check email address against whitelist"
    )
    parser_check.add_argument("email")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    return args


def add_pattern(pattern: str, comment: Optional[str]) -> None:
    with transaction.manager:
        allowed_email_pattern = (
            DBSession.query(AllowedEmailPattern).filter_by(pattern=pattern).first()
        )
        if allowed_email_pattern is not None:
            print(f"Pattern {pattern} already exists", file=sys.stderr)
            sys.exit(1)
        WhitelistAdd.create(email_pattern=pattern, comment=comment)


def list_patterns() -> None:
    for p in sorted(DBSession.query(AllowedEmailPattern), key=attrgetter("created_at")):
        print(p.created_at.isoformat(" ")[:19], p.pattern, p.comment or "", sep="\t")


def remove_pattern(pattern: str) -> None:
    with transaction.manager:
        allowed_email_pattern = (
            DBSession.query(AllowedEmailPattern).filter_by(pattern=pattern).first()
        )
        if allowed_email_pattern is None:
            print(f"Pattern {pattern} not found", file=sys.stderr)
            sys.exit(1)
        WhitelistRemove.create(allowed_email_pattern=allowed_email_pattern)


def check_email(email: str) -> None:
    normalized_email = User.normalize_email(email)
    if User.email_is_allowed(normalized_email):
        print(f"{normalized_email} is allowed by whitelist")
    else:
        print(f"{normalized_email} is not allowed by whitelist")
