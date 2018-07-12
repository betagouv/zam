from datetime import datetime

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.models import DBSession, Amendement as AmendementModel, Lecture


@view_defaults(route_name="amendement_edit")
class AmendementEdit:
    def __init__(self, request: Request) -> None:
        self.request = request
        self.lecture = Lecture.get(
            chambre=request.matchdict["chambre"],
            session=request.matchdict["session"],
            num_texte=int(request.matchdict["num_texte"]),
            organe=request.matchdict["organe"],
        )
        if self.lecture is None:
            raise HTTPBadRequest

        num = int(request.matchdict["num"])
        self.amendement = (
            DBSession.query(AmendementModel)
            .filter(
                AmendementModel.chambre == self.lecture.chambre,
                AmendementModel.session == self.lecture.session,
                AmendementModel.num_texte == self.lecture.num_texte,
                AmendementModel.organe == self.lecture.organe,
                AmendementModel.num == num,
            )
            .first()
        )
        if self.amendement is None:
            raise HTTPNotFound

    @view_config(request_method="POST")
    def post(self) -> Response:
        if int(self.request.POST["bookmark"]):
            self.amendement.bookmarked_at = datetime.utcnow()
        else:
            self.amendement.bookmarked_at = None
        return HTTPFound(
            location=self.request.resource_url(
                self.request.root["lectures"][self.amendement.url_key], "amendements"
            )
        )
