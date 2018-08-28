import pickle
from typing import Any, Dict

from pyramid.config import Configurator
from redis import Redis

from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import (
    get_dossiers_legislatifs
)
from zam_repondeur.fetch.an.organes_acteurs import get_organes_acteurs


def includeme(config: Configurator) -> None:
    """
    Called automatically via config.include("zam_repondeur.data")
    """
    repository = init_repository(config.registry.settings)
    repository.clear_data()
    repository.load_data()


_repository = None


class DataRepository:
    """
    Store and access global data in Redis
    """

    def __init__(self, redis_url: str, current_legislature: int) -> None:
        self.connection = Redis.from_url(redis_url)
        self.current_legislature = current_legislature

    def clear_data(self) -> None:
        self.connection.flushdb()

    def load_data(self) -> None:
        dossiers = get_dossiers_legislatifs(legislature=self.current_legislature)
        organes, acteurs = get_organes_acteurs(legislature=self.current_legislature)
        self.connection.set("dossiers", pickle.dumps(dossiers))
        self.connection.set("organes", pickle.dumps(organes))
        self.connection.set("acteurs", pickle.dumps(acteurs))

    def get_data(self, key: str) -> dict:
        raw_bytes = self.connection.get(key)
        if raw_bytes is None:
            return {}

        data: dict = pickle.loads(raw_bytes)
        return data


def init_repository(settings: Dict[str, Any]) -> DataRepository:
    global _repository
    _repository = DataRepository(
        redis_url=settings["zam.data.redis_url"],
        current_legislature=int(settings["zam.legislature"]),
    )
    return _repository


def load_data() -> None:
    if _repository is None:
        raise RuntimeError("You need to call init_repository() first")
    _repository.load_data()


def get_data(key: str) -> dict:
    if _repository is None:
        raise RuntimeError("You need to call init_repository() first")
    return _repository.get_data(key)
