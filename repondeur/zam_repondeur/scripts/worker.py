import logging
import os
import sys
from typing import Dict, List

import rollbar
from pyramid.paster import get_appsettings, setup_logging
from rollbar.logger import RollbarHandler
from sqlalchemy import engine_from_config

from zam_repondeur.data import init_repository
from zam_repondeur.models import DBSession
from zam_repondeur.tasks.huey import init_huey


def usage(argv: List[str]) -> None:
    cmd = os.path.basename(argv[0])
    print("usage: %s <config_uri>\n" '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv: List[str] = sys.argv) -> None:
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]

    setup_logging(config_uri)

    settings = get_appsettings(config_uri)

    rollbar_settings = extract_settings(settings, prefix="rollbar.")
    if "access_token" in rollbar_settings and "environment" in rollbar_settings:
        setup_rollbar_error_reporting(rollbar_settings)

    engine = engine_from_config(settings, "sqlalchemy.")
    DBSession.configure(bind=engine)

    init_repository(settings)

    huey = init_huey(settings)

    from zam_repondeur.tasks.fetch import fetch_articles, fetch_amendements  # noqa
    from zam_repondeur.tasks.periodic import update_data, fetch_all_amendements  # noqa

    consumer = huey.create_consumer(worker_type="thread", workers=1, max_delay=5.0)
    consumer.run()


def extract_settings(settings: Dict[str, str], prefix: str) -> Dict[str, str]:
    prefix_length = len(prefix)
    return {
        key[prefix_length:]: settings[key] for key in settings if key.startswith(prefix)
    }


def setup_rollbar_error_reporting(rollbar_settings: Dict[str, str]) -> None:
    """
    All log messages with level ERROR or higher will be sent to Rollbar
    """
    rollbar.init(**rollbar_settings)

    rollbar_handler = RollbarHandler()
    rollbar_handler.setLevel(logging.ERROR)

    root_logger = logging.getLogger()
    root_logger.addHandler(rollbar_handler)
