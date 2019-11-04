from datetime import datetime
from typing import Optional

from pyramid.config import Configurator

from zam_repondeur.initialize import needs_init
from zam_repondeur.services import Repository


def includeme(config: Configurator) -> None:
    """
    Called automatically via config.include("zam_repondeur.services.amendements")
    """
    repository.initialize(
        redis_url=config.registry.settings["zam.amendements.redis_url"]
    )


class AmendementsRepository(Repository):
    """
    Store and access global amendements in Redis
    """

    @needs_init
    def clear_data(self) -> None:
        self.connection.flushdb()

    @needs_init
    def get_last_activity_time(self, pk: int) -> Optional[datetime]:
        timestamp_bytes = self.connection.hget(str(pk), "timestamp")
        if timestamp_bytes:
            return datetime.strptime(timestamp_bytes.decode(), "%Y-%m-%dT%H:%M:%S")
        else:
            return None

    @needs_init
    def start_editing(self, pk: int, user_pk: int) -> None:
        timestamp = datetime.utcnow().isoformat(timespec="seconds")
        data = {"timestamp": timestamp, "user_pk": user_pk}
        self.connection.hmset(str(pk), data)

    @needs_init
    def stop_editing(self, pk: int) -> None:
        self.connection.delete(str(pk))


repository = AmendementsRepository()
