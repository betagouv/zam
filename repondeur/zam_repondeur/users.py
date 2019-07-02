from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from pyramid.config import Configurator
from redis import Redis
from redis.exceptions import WatchError

from .initialize import needs_init


def includeme(config: Configurator) -> None:
    """
    Called automatically via config.include("zam_repondeur.users")
    """
    repository.initialize(
        redis_url=config.registry.settings["zam.users.redis_url"],
        auth_token_duration=config.registry.settings["zam.users.auth_token_duration"],
    )


class TokenAlreadyExists(Exception):
    pass


class UsersRepository:
    """
    Store and access global users in Redis
    """

    def __init__(self) -> None:
        self.initialized = True

    def initialize(self, redis_url: str, auth_token_duration: str) -> None:
        self.connection = Redis.from_url(redis_url)
        self.auth_token_duration = int(auth_token_duration)
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

    @needs_init
    def set_auth_token(self, email: str, token: str) -> None:
        key = self._auth_key(token)
        expires_at = self.now() + timedelta(seconds=self.auth_token_duration)
        pipe = self.connection.pipeline()
        try:
            pipe.watch(key)  # detect race condition with other thread/process
            if pipe.exists(key):
                pipe.unwatch()
                raise TokenAlreadyExists
            pipe.multi()  # start transaction
            pipe.hmset(
                key, {"email": email, "expires_at": self.to_timestamp(expires_at)}
            )
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

    @staticmethod
    def now() -> datetime:
        return datetime.now(tz=timezone.utc)

    @staticmethod
    def from_timestamp(timestamp: float) -> datetime:
        return datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=timestamp)

    @staticmethod
    def to_timestamp(dt: datetime) -> float:
        return (dt - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()


repository = UsersRepository()
