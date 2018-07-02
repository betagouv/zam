from pyramid.config import Configurator
from pyramid.router import Router
from pyramid.session import SignedCookieSessionFactory
from sqlalchemy import engine_from_config

from zam_repondeur.data import load_data
from zam_repondeur.models import DBSession, Base


def make_app(global_settings: dict, **settings: dict) -> Router:

    session_factory = SignedCookieSessionFactory(settings["zam.secret"])

    with Configurator(settings=settings, session_factory=session_factory) as config:

        config.include("pyramid_tm")

        engine = engine_from_config(settings, "sqlalchemy.")
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine
        config.include("pyramid_default_cors")

        config.include("pyramid_jinja2")
        config.add_jinja2_renderer(".html")
        config.add_jinja2_search_path("zam_repondeur:templates", name=".html")

        config.add_route("home", "/")
        config.add_route("lectures_list", "/lectures/")
        config.add_route("lectures_add", "/lectures/add")

        config.add_route(
            "lecture", "/lectures/{chambre}/{session}/{num_texte:\d+}/{organe}/"
        )
        config.add_route(
            "list_reponses",
            "/lectures/{chambre}/{session}/{num_texte:\d+}/{organe}/reponses",
            "lecture_check",
            "/lectures/{chambre}/{session}/{num_texte:\d+}/{organe}/check",
        )

        config.add_route(
            "list_amendements",
            "/lectures/{chambre}/{session}/{num_texte:\d+}/{organe}/amendements/list",
        )
        config.add_route(
            "fetch_amendements",
            "/lectures/{chambre}/{session}/{num_texte:\d+}/{organe}/amendements/fetch",
        )
        config.add_route(
            "fetch_articles",
            "/lectures/{chambre}/{session}/{num_texte:\d+}/{organe}/articles/fetch",
        )
        config.add_route(
            "download_amendements",
            "/lectures/{chambre}/{session}/{num_texte:\d+}/{organe}/amendements/download.{format:(csv|xlsx)}",  # noqa
        )

        config.add_route(
            "reponse_edit",
            "/lectures/{chambre}/{session}/{num_texte:\d+}/{organe}/amendements/{num:\d+}/reponse",  # noqa
        )

        config.add_static_view("static", "static", cache_max_age=3600)

        config.scan()

        load_data(config)

        app = config.make_wsgi_app()

    return app
