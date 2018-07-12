from pyramid.config import Configurator
from pyramid.router import Router
from pyramid.session import SignedCookieSessionFactory
from sqlalchemy import engine_from_config

from zam_repondeur.data import load_data
from zam_repondeur.models import DBSession, Base
from zam_repondeur.resources import Root
from zam_repondeur.version import load_version


def make_app(global_settings: dict, **settings: dict) -> Router:

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

        config.add_route(
            "article_edit",
            "/lectures/{chambre}.{session}.{num_texte:\d+}.{organe}/articles/{subdiv_type}/{subdiv_num:.*}/{subdiv_mult:.*}/{subdiv_pos:.*}",  # noqa
        )
        config.add_route(
            "reponse_edit",
            "/lectures/{chambre}.{session}.{num_texte:\d+}.{organe}/amendements/{num:\d+}/reponse",  # noqa
        )
        config.add_route(
            "amendement_edit",
            "/lectures/{chambre}.{session}.{num_texte:\d+}.{organe}/amendements/{num:\d+}",  # noqa
        )

        config.add_static_view("static", "static", cache_max_age=3600)

        config.scan()

        load_data(config)
        load_version(config)

        app = config.make_wsgi_app()

    return app
