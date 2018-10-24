import logging
from typing import Dict

import rollbar
from rollbar.logger import RollbarHandler


def extract_settings(settings: Dict[str, str], prefix: str) -> Dict[str, str]:
    prefix_length = len(prefix)
    return {
        key[prefix_length:]: settings[key] for key in settings if key.startswith(prefix)
    }


def setup_rollbar_log_handler(rollbar_settings: Dict[str, str]) -> None:
    """
    All log messages with level ERROR or higher will be sent to Rollbar
    """
    rollbar.init(**rollbar_settings)

    rollbar_handler = RollbarHandler()
    rollbar_handler.setLevel(logging.ERROR)

    root_logger = logging.getLogger()
    root_logger.addHandler(rollbar_handler)
