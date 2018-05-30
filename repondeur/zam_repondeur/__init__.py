from pyramid.config import Configurator
from pyramid.router import Router


def make_app(global_settings: dict, **settings: dict) -> Router:
    with Configurator(settings=settings) as config:
        config.include("pyramid_jinja2")
        config.add_jinja2_renderer(".html")
        config.add_jinja2_search_path("zam_repondeur:templates", name=".html")
        config.add_route("home", "/")
        config.add_route("lectures_list", "/lectures/")
        config.add_route("lectures_add", "/lectures/add")
        config.add_route("lecture", "/lectures/{chambre}/{session}/{num_texte}/")
        config.add_route(
            "amendements_csv",
            "/lectures/{chambre}/{session}/{num_texte}/amendements.csv",
        )
        config.add_route(
            "amendements_xlsx",
            "/lectures/{chambre}/{session}/{num_texte}/amendements.xlsx",
        )
        config.scan()
        app = config.make_wsgi_app()
    return app
