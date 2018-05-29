from pyramid.request import Request
from pyramid.view import view_config


@view_config(route_name="home", renderer="index.html")
def home(request: Request) -> dict:
    return {}
