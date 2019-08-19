import pickle  # nosec
from typing import Dict, List

from pyramid.config import Configurator
from redis import Redis
from redis_lock import Lock

from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import (
    get_dossiers_legislatifs_and_textes,
)
from zam_repondeur.fetch.an.organes_acteurs import get_organes_acteurs
from zam_repondeur.fetch.senat.scraping import get_dossiers_senat

from .initialize import needs_init


def includeme(config: Configurator) -> None:
    """
    Called automatically via config.include("zam_repondeur.data")
    """
    init_repository(config.registry.settings)


def init_repository(settings: Dict[str, str]) -> None:
    repository.initialize(
        redis_url=settings["zam.data.redis_url"],
        legislatures=[int(legi) for legi in settings["zam.legislatures"].split(",")],
    )


class DataRepository:
    """
    Store and access global data in Redis

    We use a lock so that periodic updates by a worker thread do not interfere
    with regular read accesses (e.g. when fetching amendements).
    """

    def __init__(self) -> None:
        self.initialized = True

    def initialize(self, redis_url: str, legislatures: List[int]) -> None:
        self.legislatures = legislatures
        self.connection = Redis.from_url(redis_url)
        self.initialized = True

    @needs_init
    def load_data(self) -> None:
        dossiers, textes = get_dossiers_legislatifs_and_textes(*self.legislatures)
        organes, acteurs = get_organes_acteurs()
        dossiers_senat = get_dossiers_senat()
        with Lock(self.connection, "data"):
            self.connection.delete("dossiers", "organes", "acteurs")  # remove old keys
            self.connection.set("an.opendata.dossiers", pickle.dumps(dossiers))
            self.connection.set("an.opendata.textes", pickle.dumps(textes))
            self.connection.set("an.opendata.organes", pickle.dumps(organes))
            self.connection.set("an.opendata.acteurs", pickle.dumps(acteurs))
            self.connection.set("senat.scraping.dossiers", pickle.dumps(dossiers_senat))

    @needs_init
    def get_data(self, key: str) -> dict:
        with Lock(self.connection, "data"):
            raw_bytes = self.connection.get(key)
        if raw_bytes is None:
            return {}

        data: dict = pickle.loads(raw_bytes)  # nosec (not arbitrary data)
        return data


repository = DataRepository()
