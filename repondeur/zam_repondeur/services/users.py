from datetime import datetime, timedelta
from typing import Dict, Optional

from pyramid.config import Configurator
from redis.exceptions import WatchError

from zam_repondeur.initialize import needs_init
from zam_repondeur.services import Repository


def includeme(config: Configurator) -> None:
    """
    Called automatically via config.include("zam_repondeur.services.users")
    """
    repository.initialize(redis_url=config.registry.settings["zam.users.redis_url"])
    repository.auth_token_duration = int(
        config.registry.settings["zam.users.auth_token_duration"]
    )


class TokenAlreadyExists(Exception):
    pass


class UsersRepository(Repository):
    """
    Store and access global users in Redis
    """

    auth_token_duration = 0

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

    @needs_init
    def set_auth_token(self, email: str, token: str) -> None:
        key = self._auth_key(token)
        expires_at = self.to_timestamp(
            self.now() + timedelta(seconds=self.auth_token_duration)
        )
        pipe = self.connection.pipeline()
        try:
            pipe.watch(key)  # detect race condition with other thread/process
            if pipe.exists(key):
                pipe.unwatch()
                raise TokenAlreadyExists
            pipe.multi()  # start transaction
            pipe.hmset(key, {"email": email, "expires_at": expires_at})
            pipe.expireat(key, expires_at)
            pipe.execute()  # execute transaction atomically
        except WatchError:
            raise TokenAlreadyExists

    @needs_init
    def get_auth_token_data(self, token: str) -> Optional[Dict[str, str]]:
        key = self._auth_key(token)
        auth = self.connection.hgetall(key)
        if auth == {}:  # does not exist, or expired in Redis
            return None

        # Double check expiration
        expires_at = self.from_timestamp(float(auth[b"expires_at"]))
        if self.now() >= expires_at:
            return None

        return {
            key.decode("utf-8"): value.decode("utf-8") for key, value in auth.items()
        }

    @needs_init
    def delete_auth_token(self, token: str) -> None:
        key = self._auth_key(token)
        self.connection.delete(key)

    @staticmethod
    def _auth_key(token: str) -> str:
        return f"auth-{token}"


repository = UsersRepository()
