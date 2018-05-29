from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.router import Router
from pyramid.view import view_config


@view_config(route_name="home", renderer="string")
def home(request: Request) -> str:
    return "Hello world"


def make_app(global_settings: dict, **settings: dict) -> Router:
    with Configurator(settings=settings) as config:
        config.add_route("home", "/")
        config.scan()
        app = config.make_wsgi_app()
    return app
