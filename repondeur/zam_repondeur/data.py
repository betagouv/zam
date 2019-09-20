import json
import pickle  # nosec
from typing import Any, Dict, List, Optional

from pyramid.config import Configurator
from redis import Redis
from redis_lock import Lock, reset_all

from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import (
    get_dossiers_legislatifs_and_textes,
)
from zam_repondeur.fetch.an.dossiers.models import DossierRef, TexteRef
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
    def reset_locks(self) -> None:
        reset_all(self.connection)

    @needs_init
    def load_data(self) -> None:
        self._load_opendata_organes_acteurs()
        self._load_opendata_dossiers_textes()
        self._load_scraping_senat_dossiers()

    def _load_opendata_organes_acteurs(self) -> None:
        organes, acteurs = get_organes_acteurs()
        with Lock(self.connection, "data"):
            for uid, organe in organes.items():
                self._set_json_data(self._key_for_opendata_organe(uid), organe)

            for uid, acteur in acteurs.items():
                self._set_json_data(self._key_for_opendata_acteur(uid), acteur)

    def _load_opendata_dossiers_textes(self) -> None:
        dossiers, textes = get_dossiers_legislatifs_and_textes(*self.legislatures)
        with Lock(self.connection, "data"):
            for dossier_ref in dossiers.values():
                self.set_opendata_dossier_ref(dossier_ref)

            for texte_ref in textes.values():
                self.set_opendata_texte_ref(texte_ref)

    def _load_scraping_senat_dossiers(self) -> None:
        dossiers_senat = get_dossiers_senat()
        with Lock(self.connection, "data"):
            for uid, dossier_ref in dossiers_senat.items():
                self._set_pickled_data(
                    self._key_for_senat_scraping_dossier(uid), dossier_ref
                )

    def set_opendata_dossier_ref(self, dossier_ref: DossierRef) -> None:
        key = self._key_for_opendata_dossier(dossier_ref.uid)
        self._set_pickled_data(key, dossier_ref)

    def set_opendata_texte_ref(self, texte_ref: TexteRef) -> None:
        key = self._key_for_opendata_texte(texte_ref.uid)
        self._set_pickled_data(key, texte_ref)

    @staticmethod
    def _key_for_opendata_dossier(uid: str) -> str:
        return f"an.opendata.dossiers.{uid}"

    @staticmethod
    def _key_for_opendata_texte(uid: str) -> str:
        return f"an.opendata.textes.{uid}"

    @staticmethod
    def _key_for_opendata_organe(uid: str) -> str:
        return f"an.opendata.organes.{uid}"

    @staticmethod
    def _key_for_opendata_acteur(uid: str) -> str:
        return f"an.opendata.acteurs.{uid}"

    @staticmethod
    def _key_for_senat_scraping_dossier(uid: str) -> str:
        return f"senat.scraping.dossiers.{uid}"

    @needs_init
    def get_opendata_organe(self, uid: str) -> dict:
        key = self._key_for_opendata_organe(uid)
        organe: dict = self._get_json_data(key)
        return organe

    @needs_init
    def get_opendata_acteur(self, uid: str) -> dict:
        key = self._key_for_opendata_acteur(uid)
        acteur: dict = self._get_json_data(key)
        return acteur

    @needs_init
    def get_opendata_dossier(self, uid: str) -> DossierRef:
        key = self._key_for_opendata_dossier(uid)
        dossier_ref: DossierRef = self._get_pickled_data(key)
        return dossier_ref

    @needs_init
    def list_opendata_dossiers(self) -> List[str]:
        keys = self.connection.keys(self._key_for_opendata_dossier("*"))
        return [key.decode("utf-8").split(".")[-1] for key in keys]

    @needs_init
    def list_opendata_textes(self) -> List[str]:
        keys = self.connection.keys(self._key_for_opendata_texte("*"))
        return [key.decode("utf-8").split(".")[-1] for key in keys]

    @needs_init
    def list_senat_scraping_dossiers(self) -> List[str]:
        keys = self.connection.keys(self._key_for_senat_scraping_dossier("*"))
        return [key.decode("utf-8").split(".")[-1] for key in keys]

    @needs_init
    def get_opendata_texte(self, uid: str) -> TexteRef:
        key = self._key_for_opendata_texte(uid)
        texte_ref: TexteRef = self._get_pickled_data(key)
        return texte_ref

    @needs_init
    def get_senat_scraping_dossier(self, uid: str) -> DossierRef:
        key = self._key_for_senat_scraping_dossier(uid)
        dossier_ref: DossierRef = self._get_pickled_data(key)
        return dossier_ref

    @needs_init
    def get_dossier_ref(self, uid: str) -> DossierRef:
        return self.get_opendata_dossier(uid) or self.get_senat_scraping_dossier(uid)

    @needs_init
    def _set_pickled_data(self, key: str, value: Any) -> None:
        self.connection.set(key, pickle.dumps(value))

    @needs_init
    def _get_pickled_data(self, key: str) -> Any:
        raw_bytes = self._get_raw_data(key)
        if raw_bytes is None:
            return None
        return pickle.loads(raw_bytes)  # nosec (not arbitrary data)

    @needs_init
    def _set_json_data(self, key: str, value: Any) -> None:
        self.connection.set(key, json.dumps(value))

    @needs_init
    def _get_json_data(self, key: str) -> Any:
        raw_bytes = self._get_raw_data(key)
        if raw_bytes is None:
            return None
        return json.loads(raw_bytes)

    @needs_init
    def _get_raw_data(self, key: str) -> Optional[bytes]:
        with Lock(self.connection, "data"):
            response: Optional[bytes] = self.connection.get(key)
            return response


repository = DataRepository()
