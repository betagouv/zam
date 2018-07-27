from pyramid.config import Configurator
from pyramid.threadlocal import get_current_registry

from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import (
    get_dossiers_legislatifs
)
from zam_repondeur.fetch.an.organes_acteurs import get_organes_acteurs


def load_data(config: Configurator) -> None:
    data = config.registry.settings.setdefault("data", {})
    current_legislature = int(config.registry.settings["zam.legislature"])
    data["dossiers"] = get_dossiers_legislatifs(legislature=current_legislature)
    organes, acteurs = get_organes_acteurs(legislature=current_legislature)
    data["organes"] = organes
    data["acteurs"] = acteurs


def get_data(key: str) -> dict:
    registry = get_current_registry()
    settings = registry.settings
    data: dict = settings["data"][key]
    return data
