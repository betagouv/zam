from pyramid.request import Request
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config
from redis.exceptions import ConnectionError
from sqlalchemy.exc import OperationalError

from zam_repondeur.models import DBSession
from zam_repondeur.services.data import repository
from zam_repondeur.tasks.huey import huey


def get_db_version() -> str:
    return str(DBSession.execute("SELECT version();").first()["version"])


def get_redis_infos() -> str:
    redis_infos = repository.connection.info()
    redis_keys = ", ".join(
        f"{k}: {v['keys']} keys" for k, v in redis_infos.items() if k.startswith("db")
    )
    return f"{redis_infos['redis_version']} ({redis_keys})"


def get_huey_infos() -> str:
    return f"{huey.storage.queue_size()} items in queue"


@view_config(route_name="monitoring", permission=NO_PERMISSION_REQUIRED)
def monitoring(request: Request) -> Response:

    try:
        db_infos = f"OK - {get_db_version()}"
    except OperationalError:
        db_infos = "KO"

    try:
        redis_infos = f"OK - {get_redis_infos()}"
    except ConnectionError:
        redis_infos = "KO"

    try:
        huey_infos = f"OK - {get_huey_infos()}"
    except ConnectionError:
        huey_infos = "KO"

    return Response(
        f"""
App: OK<br>
DB: {db_infos}<br>
Redis: {redis_infos}<br>
Huey: {huey_infos}<br>
        """
    )
