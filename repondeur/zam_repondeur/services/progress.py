from datetime import timedelta
from typing import Dict, Optional

from pyramid.config import Configurator

from zam_repondeur.initialize import needs_init
from zam_repondeur.services import Repository


def includeme(config: Configurator) -> None:
    """
    Called automatically via config.include("zam_repondeur.services.progress")
    """
    repository.initialize(redis_url=config.registry.settings["zam.progress.redis_url"])
    repository.max_duration = int(config.registry.settings["zam.progress.max_duration"])


class ProgressRepository(Repository):
    """
    Store and access progress of Lecture retrieval/update
    """

    max_duration = 0

    @needs_init
    def clear_data(self) -> None:
        self.connection.flushdb()

    @staticmethod
    def _key_for_progress(lecture_pk: str) -> str:
        return f"fetch.progress.{lecture_pk}"

    @needs_init
    def set_fetch_progress(self, lecture_pk: str, current: int, total: int) -> None:
        key = self._key_for_progress(lecture_pk)
        expires_at = self.to_timestamp(
            self.now() + timedelta(seconds=self.max_duration * 60)
        )
        self.connection.hmset(key, {"current": current, "total": total})
        self.connection.expireat(key, expires_at)

    @needs_init
    def reset_fetch_progress(self, lecture_pk: str) -> None:
        key = self._key_for_progress(lecture_pk)
        self.connection.hdel(key, "current", "total")

    @needs_init
    def get_fetch_progress(self, lecture_pk: str) -> Optional[Dict[str, int]]:
        key = self._key_for_progress(lecture_pk)
        progress: Optional[Dict[str, int]] = {
            key.decode(): int(value)
            for key, value in self.connection.hgetall(key).items()
        }
        return progress


repository = ProgressRepository()
