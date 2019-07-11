import logging
import sys
from argparse import ArgumentParser, Namespace
from typing import Any, Dict, List

from huey import Huey
from pyramid.paster import bootstrap, setup_logging
from redis.exceptions import ConnectionError

from zam_repondeur.errors import extract_settings, setup_rollbar_log_handler


logger = logging.getLogger(__name__)


def main(argv: List[str] = sys.argv) -> None:

    args = parse_args(argv[1:])

    setup_logging(args.config_uri)

    options = {"app": "zam_worker"}

    with bootstrap(args.config_uri, options=options) as env:
        settings = env["registry"].settings
        request = env["request"]

        rollbar_settings = extract_settings(settings, prefix="rollbar.")
        if "access_token" in rollbar_settings and "environment" in rollbar_settings:
            setup_rollbar_log_handler(rollbar_settings)

        start_huey(args.config_uri, options, settings, request.huey)


def start_huey(
    config_uri: str, options: Dict[str, str], settings: Dict[str, Any], huey: Huey
) -> None:
    from zam_repondeur.tasks.fetch import (  # noqa
        fetch_articles,
        fetch_amendements,
        fetch_lectures,
    )
    from zam_repondeur.tasks.periodic import update_data, fetch_all_lectures  # noqa

    try:
        flush_stale_locks(huey)
    except ConnectionError:
        logger.exception("Failed to connect to Redis")
        sys.exit(1)

    @huey.on_startup()
    def startup_hook() -> None:
        bootstrap(config_uri, options=options)

    consumer = huey.create_consumer(
        worker_type="thread",
        workers=int(settings["huey.workers"]),
        max_delay=5.0,
        flush_locks=True,
    )
    consumer.run()


def parse_args(argv: List[str]) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("config_uri")
    return parser.parse_args(argv)


def flush_stale_locks(huey: Huey) -> None:
    """
    Flush stale Huey locks

    Huey can only flush static locks (those used in a decorator) by himself,
    not dynamic locks (those used in context managers) so we have to dig into
    the Redis data structure to remove them ourselves.

    cf. https://github.com/coleifer/huey/issues/308#issuecomment-379142489
    """
    redis_conn = huey.storage.conn
    results = redis_conn.hgetall("huey.results.huey")
    locks = [key for key in results.keys() if key.startswith(b"huey.lock.")]
    if locks:
        logger.info("Found stale locks: %r", locks)
        response = redis_conn.hdel("huey.results.huey", *locks)
        if response == len(locks):
            logger.info("All locks removed successfully")
        else:
            logger.warning("Unexpected result from Redis: %r", response)
    return
