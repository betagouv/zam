from pyramid.view import exception_view_config
from pyramid.httpexceptions import HTTPNotFound
from pyramid.request import Request
from pyramid.response import Response

from zam_repondeur.resources import ResourceNotFound


@exception_view_config(ResourceNotFound)
def resource_not_found(exc: ResourceNotFound, request: Request) -> Response:
    return HTTPNotFound()
