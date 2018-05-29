from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name="home")
def home(request: Request) -> Response:
    return HTTPFound(location=request.route_url("textes_list"))
