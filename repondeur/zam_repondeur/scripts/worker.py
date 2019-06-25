import logging
import sys
from argparse import ArgumentParser, Namespace
from typing import Any, Dict, List

from huey import RedisHuey
from pyramid.paster import get_appsettings, setup_logging
from redis.exceptions import ConnectionError
from sqlalchemy import engine_from_config

from zam_repondeur import BASE_SETTINGS
from zam_repondeur.data import init_repository
from zam_repondeur.errors import extract_settings, setup_rollbar_log_handler
from zam_repondeur.models import DBSession
from zam_repondeur.tasks.huey import init_huey


logger = logging.getLogger(__name__)


def main(argv: List[str] = sys.argv) -> None:
    args = parse_args(argv[1:])

    setup_logging(args.config_uri)

    settings = get_appsettings(args.config_uri)
    settings = {**BASE_SETTINGS, **settings}

    rollbar_settings = extract_settings(settings, prefix="rollbar.")
    if "access_token" in rollbar_settings and "environment" in rollbar_settings:
        setup_rollbar_log_handler(rollbar_settings)

    engine = engine_from_config(
        settings, "sqlalchemy.", connect_args={"application_name": "zam_worker"}
    )

    DBSession.configure(bind=engine)

    init_repository(settings)

    start_huey(settings)


def start_huey(settings: Dict[str, Any]) -> None:
    huey = init_huey(settings)

    from zam_repondeur.tasks.fetch import fetch_articles, fetch_amendements  # noqa
    from zam_repondeur.tasks.periodic import update_data, fetch_all_amendements  # noqa

    try:
        flush_stale_locks(huey)
    except ConnectionError:
        logger.exception("Failed to connect to Redis")
        sys.exit(1)

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


def flush_stale_locks(huey: RedisHuey) -> None:
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
