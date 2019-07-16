from huey.api import Huey, RedisStorage
from paste.deploy.converters import asbool

from .queue import TransactionalHuey

huey: TransactionalHuey = None  # type: ignore


def init_huey(settings: dict) -> Huey:
    global huey
    if huey is None:
        huey = TransactionalHuey(
            storage_class=RedisStorage,
            url=settings["zam.tasks.redis_url"],
            immediate=asbool(settings.get("zam.tasks.immediate", "False")),
        )
    return huey
