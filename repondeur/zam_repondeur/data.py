import pickle

from redis import Redis

from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import (
    get_dossiers_legislatifs
)
from zam_repondeur.fetch.an.organes_acteurs import get_organes_acteurs


def load_data(settings: dict, connection: Redis) -> None:
    current_legislature = int(settings["zam.legislature"])
    dossiers = get_dossiers_legislatifs(legislature=current_legislature)
    organes, acteurs = get_organes_acteurs(legislature=current_legislature)
    connection.set("dossiers", pickle.dumps(dossiers))
    connection.set("organes", pickle.dumps(organes))
    connection.set("acteurs", pickle.dumps(acteurs))


def get_data(key: str) -> dict:
    from zam_repondeur import huey

    raw_bytes = huey.storage.conn.get(key)
    if raw_bytes is None:
        return {}

    data: dict = pickle.loads(raw_bytes)
    return data
