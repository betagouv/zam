from multiprocessing import cpu_count
from typing import Any

from paste.deploy.converters import asbool
from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.router import Router
from pyramid.session import JSONSerializer, SignedCookieSessionFactory
from pyramid.view import view_config
from sqlalchemy import engine_from_config, event

from zam_repondeur.errors import extract_settings, setup_rollbar_log_handler
from zam_repondeur.models import DBSession, Base, log_query_with_origin
from zam_repondeur.resources import Root
from zam_repondeur.tasks.huey import init_huey
from zam_repondeur.version import load_version


FILTERS_PATH = "zam_repondeur.views.jinja2_filters"
BASE_SETTINGS = {
    "jinja2.filters": {
        "paragriphy": f"{FILTERS_PATH}:paragriphy",
        "amendement_matches": f"{FILTERS_PATH}:amendement_matches",
        "filter_out_empty_additionals": f"{FILTERS_PATH}:filter_out_empty_additionals",
        "group_by_day": f"{FILTERS_PATH}:group_by_day",
        "h3_to_h5": f"{FILTERS_PATH}:h3_to_h5",
    },
    "jinja2.undefined": "strict",
    "zam.auth_cookie_duration": 7 * 24 * 3600,  # a user stays identified for 7 days
    "zam.auth_cookie_secure": True,  # disable for local HTTP access in development
    "zam.legislatures": "14,15",
    "huey.workers": (cpu_count() * 2) + 1,
    # Intervals in seconds for notifications checks:
    # Keep it low: potential data loss for the user.
    "zam.check_for.amendement_stolen_while_editing": 30,
    # Keep it low: critical during public intervention.
    "zam.check_for.content_updated_during_seance": 30,
    "zam.check_for.transfers_from_to_my_table": 60,
    # Keep it high: lot of modifications happen in the meantime.
    "zam.check_for.index_updates": 180,
}


def make_app(global_settings: dict, **settings: Any) -> Router:

    settings = {**BASE_SETTINGS, **settings}

    session_factory = SignedCookieSessionFactory(
        secret=settings["zam.session_secret"], serializer=JSONSerializer()
    )

    with Configurator(
        settings=settings, root_factory=Root, session_factory=session_factory
    ) as config:

        rollbar_settings = extract_settings(settings, prefix="rollbar.")
        if "access_token" in rollbar_settings and "environment" in rollbar_settings:
            setup_rollbar_log_handler(rollbar_settings)

        setup_database(config, settings)

        config.include("zam_repondeur.auth")

        config.include("pyramid_default_cors")

        config.include("pyramid_jinja2")
        config.add_jinja2_renderer(".html")
        config.add_jinja2_search_path("zam_repondeur:templates", name=".html")

        config.add_route("choices_lectures", "/choices/dossiers/{uid}/")
        config.add_route("error", "/error")

        config.include("zam_repondeur.assets")

        init_huey(settings)
        config.include("zam_repondeur.data")
        config.include("zam_repondeur.users")
        load_version(config)

        config.scan()

        app = config.make_wsgi_app()

    return app


@view_config(route_name="error")
def error(request: Request) -> None:
    raise Exception("Not a real error (just for testing)")


def setup_database(config: Configurator, settings: dict) -> None:

    config.include("pyramid_tm")

    engine = engine_from_config(
        settings, "sqlalchemy.", connect_args={"application_name": "zam_webapp"}
    )
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    if asbool(settings.get("zam.log_sql_queries_with_origin")):
        event.listen(engine, "before_cursor_execute", log_query_with_origin)
