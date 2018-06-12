from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.models import (
    DBSession,
    Amendement as AmendementModel,
    CHAMBRES,
    AVIS,
)


@view_defaults(route_name="reponse_edit", renderer="reponse_edit.html")
class ReponseEdit:
    def __init__(self, request: Request) -> None:
        self.request = request

        chambre = request.matchdict["chambre"]
        session = request.matchdict["session"]
        num_texte = request.matchdict["num_texte"]
        num = request.matchdict["num"]
        if chambre not in CHAMBRES:
            raise HTTPBadRequest
        self.amendement = (
            DBSession.query(AmendementModel)
            .filter(
                AmendementModel.chambre == chambre,
                AmendementModel.session == session,
                AmendementModel.num_texte == num_texte,
                AmendementModel.num == num,
            )
            .first()
        )
        if self.amendement is None:
            raise HTTPNotFound

    @view_config(request_method="GET")
    def get(self) -> dict:
        return {"amendement": self.amendement, "avis": AVIS}

    @view_config(request_method="POST")
    def post(self) -> Response:
        self.amendement.avis = self.request.POST["avis"]
        self.amendement.observations = self.request.POST["observations"]
        return HTTPFound(
            location=self.request.route_url(
                "list_amendements",
                chambre=self.amendement.chambre,
                session=self.amendement.session,
                num_texte=self.amendement.num_texte,
            )
        )
