"""
Add fake amendements to an existing lecture (for performance testing)
"""
import logging
import random
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
            lecture = find_lecture(
                chambre=args.chambre,
                legislature=args.legislature,
                session=args.session,
                organe=args.organe,
                num=args.num,
                partie=args.partie,
            )
            print(lecture.dossier.titre)
            print(lecture)
            print("Initial count:", len(lecture.amendements), "amendements")
            create_fake_amendements(lecture, count=args.count)
            print("Updated count:", len(lecture.amendements), "amendements")


def parse_args(argv: List[str]) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("config_uri")
    parser.add_argument("--num", type=int, required=True, help="N° de texte")
    parser.add_argument("--partie", type=int, required=False, default=None)
    parser.add_argument("--chambre", required=True, choices=["an", "senat"])
    parser.add_argument("--legislature", type=int, required=False)
    parser.add_argument("--session", type=int, required=False)
    parser.add_argument("--organe", required=True)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("count", type=int)
    return parser.parse_args(argv)


def find_lecture(
    num: int,
    partie: Optional[int],
    chambre: str,
    legislature: Optional[int],
    session: Optional[int],
    organe: str,
) -> Lecture:
    texte = (
        DBSession.query(Texte)
        .filter_by(
            chambre=Chambre.from_string(chambre),
            legislature=legislature,
            session=session,
            numero=num,
        )
        .one()
    )
    lecture: Lecture = (
        DBSession.query(Lecture)
        .filter_by(texte=texte, partie=partie, organe=organe)
        .one()
    )
    return lecture


def create_fake_amendements(lecture: Lecture, count: int) -> None:
    start = max(int(amdt.num) for amdt in lecture.amendements) + 1
    today = date.today()
    for num in range(start, start + count):
        Amendement.create(
            lecture=lecture,
            article=random.choice(lecture.articles),  # nosec
            num=str(num),
            auteur="M. Bidon",
            date_depot=today,
            expose=(
                "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Libero "
                "explicabo laborum, natus dolorum eligendi in fuga ducimus minima "
                "minus. Impedit alias dicta obcaecati, omnis atque delectus in eius "
                "aliquid ex."
            ),
            corps=(
                "Voluptatem, tempore asperiores ducimus, repudiandae eaque ex "
                "corporis blanditiis fugiat atque tenetur incidunt commodi, "
                "veritatis qui dicta. Quibusdam tempora sint, non veritatis."
            ),
        )
    print("Added", start, "to", start + count - 1)
