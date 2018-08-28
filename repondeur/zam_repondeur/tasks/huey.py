from huey import RedisHuey
from paste.deploy.converters import asbool

huey: RedisHuey = None


def init_huey(settings: dict) -> RedisHuey:
    global huey
    huey = RedisHuey(
        url=settings["zam.tasks.redis_url"],
        always_eager=asbool(settings.get("zam.tasks.always_eager", "False")),
    )
    return huey
