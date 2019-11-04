from datetime import datetime, timedelta, timezone

from redis import Redis


class Repository:
    """Base class to initialize a repository."""

    def __init__(self) -> None:
        self.initialized = True

    def initialize(self, redis_url: str) -> "Repository":
        self.connection = Redis.from_url(redis_url)
        self.initialized = True
        return self

    @staticmethod
    def now() -> datetime:
        return datetime.now(tz=timezone.utc)

    @staticmethod
    def from_timestamp(timestamp: float) -> datetime:
        return datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=timestamp)

    @staticmethod
    def to_timestamp(dt: datetime) -> int:
        return int((dt - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
