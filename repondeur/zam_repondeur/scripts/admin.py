"""
Deal with admin statuses.
"""
import logging
import sys
from argparse import ArgumentParser, Namespace
from operator import attrgetter
from typing import List

import transaction
from pyramid.paster import bootstrap, setup_logging

from zam_repondeur.models import DBSession
from zam_repondeur.models.events.admin import AdminGrant, AdminRevoke
from zam_repondeur.models.users import User

logger = logging.getLogger(__name__)


def main(argv: List[str] = sys.argv) -> None:

    args = parse_args(argv[1:])

    setup_logging(args.config_uri)

    logging.getLogger().setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

    with bootstrap(args.config_uri, options={"app": "zam_load_data"}):
        if args.command == "grant":
            grant_admin(email=args.email)
        elif args.command == "list":
            list_admins()
        elif args.command == "revoke":
            revoke_admin(email=args.email)
        else:
            sys.exit(1)


def parse_args(argv: List[str]) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("config_uri")

    subparsers = parser.add_subparsers(dest="command", metavar="command")

    parser_grant = subparsers.add_parser(
        "grant", help="grant admin privileges to a user email"
    )
    parser_grant.add_argument("email")

    subparsers.add_parser("list", help="list admin users")

    parser_revoke = subparsers.add_parser(
        "revoke", help="revoke admin privileges to a user email"
    )
    parser_revoke.add_argument("email")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    return args


def grant_admin(email: str) -> None:
    with transaction.manager:
        user = DBSession.query(User).filter(User.email == email).first()
        if not user:
            print(f"Email {email} is not registered", file=sys.stderr)
            sys.exit(1)
        if user.is_admin:
            print(f"User {user} has already admin privileges", file=sys.stderr)
            sys.exit(1)
        AdminGrant.create(target=user)


def list_admins() -> None:
    for user in sorted(
        DBSession.query(User).filter(User.admin_at.isnot(None)),  # type: ignore
        key=attrgetter("admin_at"),
    ):
        print(user, user.admin_at, sep="\t")


def revoke_admin(email: str) -> None:
    with transaction.manager:
        user = DBSession.query(User).filter(User.email == email).first()
        if not user:
            print(f"Email {email} is not registered", file=sys.stderr)
            sys.exit(1)
        if not user.is_admin:
            print(f"User {user} has no admin privileges", file=sys.stderr)
            sys.exit(1)
        AdminRevoke.create(target=user)
