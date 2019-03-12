from datetime import datetime
from typing import Optional

from pyramid.config import Configurator
from redis import Redis

from .initialize import needs_init


def includeme(config: Configurator) -> None:
    """
    Called automatically via config.include("zam_repondeur.users")
    """
    repository.initialize(redis_url=config.registry.settings["zam.users.redis_url"])


class UsersRepository:
    """
    Store and access global users in Redis
    """

    def __init__(self) -> None:
        self.initialized = True

    def initialize(self, redis_url: str) -> None:
        self.connection = Redis.from_url(redis_url)
        self.initialized = True

    @needs_init
    def clear_data(self) -> None:
        self.connection.flushdb()

    @needs_init
    def get_last_activity_time(self, email: str) -> Optional[datetime]:
        timestamp_bytes = self.connection.get(email)
        if timestamp_bytes:
            return datetime.strptime(timestamp_bytes.decode(), "%Y-%m-%dT%H:%M:%S")
        else:
            return None

    @needs_init
    def set_last_activity_time(self, email: str) -> None:
        timestamp = datetime.utcnow().isoformat(timespec="seconds")
        self.connection.set(email, timestamp)


repository = UsersRepository()
