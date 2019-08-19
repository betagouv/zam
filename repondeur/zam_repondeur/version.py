from subprocess import STDOUT, CalledProcessError, check_output  # nosec
from typing import List

from pyramid.config import Configurator


def load_version(config: Configurator) -> None:
    config.registry.settings["version"] = {
        "branch": run(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "sha1": run(["git", "rev-parse", "HEAD"]),
        "date": run(["git", "show", "--no-patch", "--format=%ci", "HEAD"]),
    }


def run(command: List[str]) -> str:
    try:
        # This is considered safe as we only run predefined git commands
        res: bytes = check_output(command, stderr=STDOUT)  # nosec
        return res.decode("utf-8").strip()
    except CalledProcessError:
        return "unknown"
