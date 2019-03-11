from datetime import datetime
from typing import Any, Dict, Optional

from pyramid.config import Configurator
from redis import Redis


def includeme(config: Configurator) -> None:
    """
    Called automatically via config.include("zam_repondeur.users")
    """
    init_repository(config.registry.settings)


_repository = None


class UsersRepository:
    """
    Store and access global users in Redis
    """

    def __init__(self, redis_url: str) -> None:
        self.connection = Redis.from_url(redis_url)

    def clear_data(self) -> None:
        self.connection.flushdb()

    def get_last_activity_time(self, email: str) -> Optional[datetime]:
        timestamp_bytes = self.connection.get(email)
        if timestamp_bytes:
            return datetime.strptime(timestamp_bytes.decode(), "%Y-%m-%dT%H:%M:%S")
        else:
            return None

    def set_last_activity_time(self, email: str) -> None:
        timestamp = datetime.utcnow().isoformat(timespec="seconds")
        self.connection.set(email, timestamp)


def init_repository(settings: Dict[str, Any]) -> UsersRepository:
    global _repository
    _repository = UsersRepository(redis_url=settings["zam.users.redis_url"])
    return _repository


def get_last_activity_time(email: str) -> Optional[datetime]:
    if _repository is None:
        raise RuntimeError("You need to call init_repository() first")
    return _repository.get_last_activity_time(email)


def set_last_activity_time(email: str) -> None:
    if _repository is None:
        raise RuntimeError("You need to call init_repository() first")
    _repository.set_last_activity_time(email)
