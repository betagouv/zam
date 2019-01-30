from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.models import DBSession, Amendement
from zam_repondeur.resources import SpaceResource


@view_defaults(context=SpaceResource)
class SpaceView:
    def __init__(self, context: SpaceResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.lecture = context.lecture_resource.model()

    @view_config(request_method="GET", renderer="space_detail.html")
    def get(self) -> dict:
        return {"lecture": self.lecture, "amendements": self.context.amendements()}

    @view_config(request_method="POST")
    def post(self) -> Response:
        num = self.request.POST["num"]
        amendement = (
            DBSession.query(Amendement)
            .filter(Amendement.lecture == self.lecture, Amendement.num == num)
            .first()
        )
        self.request.user.space.amendements.append(amendement)
        return HTTPFound(
            location=self.request.resource_url(
                self.context.parent, self.request.user.email
            )
        )
