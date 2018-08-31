from subprocess import check_output, CalledProcessError
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
        res: bytes = check_output(command)
        return res.decode("utf-8").strip()
    except CalledProcessError:
        return "unknown"
