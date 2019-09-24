"""
Add an allowed pattern to the email authentication whitelist
"""
import logging
import sys
from argparse import ArgumentParser, Namespace
from datetime import datetime
from operator import attrgetter
from typing import List

import transaction
from pyramid.paster import bootstrap, setup_logging

from zam_repondeur.models import DBSession
from zam_repondeur.models.users import User

logger = logging.getLogger(__name__)


def main(argv: List[str] = sys.argv) -> None:

    args = parse_args(argv[1:])

    setup_logging(args.config_uri)

    logging.getLogger().setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

    with bootstrap(args.config_uri, options={"app": "zam_load_data"}):
        if args.command == "set":
            set_admin(email=args.email)
        elif args.command == "list":
            list_admins()
        elif args.command == "unset":
            unset_admin(email=args.email)
        else:
            sys.exit(1)


def parse_args(argv: List[str]) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("config_uri")

    subparsers = parser.add_subparsers(dest="command", metavar="command")

    parser_set = subparsers.add_parser("set", help="set user email as an admin")
    parser_set.add_argument("email")

    subparsers.add_parser("list", help="list admin users")

    parser_unset = subparsers.add_parser("unset", help="unset user email from an admin")
    parser_unset.add_argument("email")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    return args


def set_admin(email: str) -> None:
    with transaction.manager:
        user = DBSession.query(User).filter(User.email == email).first()
        if not user:
            print(f"Email {email} is not registered", file=sys.stderr)
            sys.exit(1)
        if user.is_admin:
            print(f"User {user} is already an admin", file=sys.stderr)
            sys.exit(1)
        user.admin_at = datetime.utcnow()


def list_admins() -> None:
    for u in sorted(
        DBSession.query(User).filter(User.admin_at.isnot(None)),  # type: ignore
        key=attrgetter("created_at"),
    ):
        print(u, u.admin_at, sep="\t")


def unset_admin(email: str) -> None:
    with transaction.manager:
        user = DBSession.query(User).filter(User.email == email).first()
        if not user:
            print(f"Email {email} is not registered", file=sys.stderr)
            sys.exit(1)
        if not user.is_admin:
            print(f"User {user} is not an admin", file=sys.stderr)
            sys.exit(1)
        user.admin_at = None
