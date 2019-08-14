from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

from zam_repondeur.resources import Root


@view_config(context=Root)
def home(context: Root, request: Request) -> Response:
    return HTTPFound(location=request.resource_url(context["dossiers"]))
