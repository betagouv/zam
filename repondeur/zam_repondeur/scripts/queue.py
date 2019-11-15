import logging
import sys
from argparse import ArgumentParser, Namespace
from typing import List

from pyramid.paster import bootstrap, setup_logging

logger = logging.getLogger(__name__)


def main(argv: List[str] = sys.argv) -> None:

    args = parse_args(argv[1:])

    setup_logging(args.config_uri)

    with bootstrap(args.config_uri, options={"app": "zam_queue"}) as env:
        request = env["request"]
        huey = request.huey
        count = huey.pending_count()
        if args.count_only:
            print(count)
        else:
            print(f"{count} task(s) in queue")
            for task in huey.pending():
                print(task)


def parse_args(argv: List[str]) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("config_uri")
    parser.add_argument(
        "-c",
        "--count-only",
        action="store_true",
        help="Only show the number of queued tasks",
    )
    return parser.parse_args(argv)
