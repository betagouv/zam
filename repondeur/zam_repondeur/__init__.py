from multiprocessing import cpu_count
from typing import Any

from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.router import Router
from pyramid.session import SignedCookieSessionFactory
from pyramid.view import view_config
from sqlalchemy import engine_from_config

from zam_repondeur.models import DBSession, Base
from zam_repondeur.resources import Root
from zam_repondeur.tasks.huey import init_huey
from zam_repondeur.version import load_version


BASE_SETTINGS = {
    "jinja2.filters": {
        "paragriphy": "zam_repondeur.views.jinja2_filters:paragriphy",
        "amendement_matches": "zam_repondeur.views.jinja2_filters:amendement_matches",
    },
    "zam.legislature": 15,
    "huey.workers": (cpu_count() * 2) + 1,
}


def make_app(global_settings: dict, **settings: Any) -> Router:

    settings = {**BASE_SETTINGS, **settings}

    session_factory = SignedCookieSessionFactory(settings["zam.secret"])

    with Configurator(
        settings=settings, root_factory=Root, session_factory=session_factory
    ) as config:

        config.include("pyramid_tm")

        engine = engine_from_config(settings, "sqlalchemy.")
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine
        config.include("pyramid_default_cors")

        config.include("pyramid_jinja2")
        config.add_jinja2_renderer(".html")
        config.add_jinja2_search_path("zam_repondeur:templates", name=".html")

        config.add_route("choices_lectures", "/choices/dossiers/{uid}/")
        config.add_route("error", "/error")

        config.include("zam_repondeur.assets")

        init_huey(settings)
        config.include("zam_repondeur.data")
        load_version(config)

        config.scan()

        app = config.make_wsgi_app()

    return app


@view_config(route_name="error")
def error(request: Request) -> None:
    raise Exception("Not a real error (just for testing)")
