import logging
from typing import Dict

import pyramid_retry
import rollbar
from pyramid.config import Configurator
from rollbar.contrib.pyramid import EXCEPTION_BLACKLIST, EXCEPTION_WHITELIST
from rollbar.logger import RollbarHandler


logger = logging.getLogger(__name__)


def includeme(config: Configurator) -> None:
    settings = config.registry.settings
    rollbar_settings = extract_settings(settings, prefix="rollbar.")
    if "access_token" in rollbar_settings and "environment" in rollbar_settings:

        # Monkey-patch Rollbar error handler function to replace it with ours
        rollbar.contrib.pyramid.handle_error = handle_error

        # Configure Rollbar integration
        config.include("rollbar.contrib.pyramid")

        # Also send log entries with level ERROR or higher
        setup_rollbar_log_handler(rollbar_settings)


def extract_settings(settings: Dict[str, str], prefix: str) -> Dict[str, str]:
    prefix_length = len(prefix)
    return {
        key[prefix_length:]: settings[key] for key in settings if key.startswith(prefix)
    }


def handle_error(request, exception, exc_info):  # type: ignore
    if isinstance(exception, EXCEPTION_BLACKLIST) and not isinstance(
        exception, EXCEPTION_WHITELIST
    ):
        return
    if pyramid_retry.is_error_retryable(request, exception):
        logging.info("Error is retryable, not sending to Rollbar")
        return
    rollbar.report_exc_info(exc_info, request)


def setup_rollbar_log_handler(rollbar_settings: Dict[str, str]) -> None:
    """
    All log messages with level ERROR or higher will be sent to Rollbar
    """
    rollbar.init(**rollbar_settings)

    rollbar_handler = RollbarHandler()
    rollbar_handler.setLevel(logging.ERROR)

    root_logger = logging.getLogger()
    root_logger.addHandler(rollbar_handler)
