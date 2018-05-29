from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.router import Router
from pyramid.view import view_config


@view_config(route_name="home", renderer="index.html")
def home(request: Request) -> dict:
    return {}


def make_app(global_settings: dict, **settings: dict) -> Router:
    with Configurator(settings=settings) as config:
        config.include("pyramid_jinja2")
        config.add_jinja2_renderer(".html")
        config.add_jinja2_search_path("zam_repondeur:templates", name=".html")
        config.add_route("home", "/")
        config.scan()
        app = config.make_wsgi_app()
    return app
