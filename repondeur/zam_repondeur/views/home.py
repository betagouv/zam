from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

from zam_repondeur.resources import Root


@view_config(context=Root)
def home(context: Root, request: Request) -> Response:
    default_resource = request.registry.settings["zam.home"]
    return HTTPFound(location=request.resource_url(context[default_resource]))
