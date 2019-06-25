from huey import RedisHuey
from paste.deploy.converters import asbool

huey: RedisHuey = None


def init_huey(settings: dict) -> RedisHuey:
    global huey
    if huey is None:
        huey = RedisHuey(
            url=settings["zam.tasks.redis_url"],
            immediate=asbool(settings.get("zam.tasks.immediate", "False")),
        )
    return huey
