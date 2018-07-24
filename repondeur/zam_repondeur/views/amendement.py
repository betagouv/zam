from datetime import datetime

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

from zam_repondeur.resources import AmendementResource


@view_config(context=AmendementResource, request_method="POST")
def update_amendement(context: AmendementResource, request: Request) -> Response:
    amendement = context.model()

    if int(request.POST["bookmark"]):
        amendement.bookmarked_at = datetime.utcnow()
    else:
        amendement.bookmarked_at = None

    return HTTPFound(location=request.resource_url(context.parent))
