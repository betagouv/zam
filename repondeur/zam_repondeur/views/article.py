from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.models import DBSession, Amendement, Lecture


@view_defaults(route_name="article_edit")
class ArticleEdit:
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

        subdiv_type = request.matchdict["subdiv_type"]
        subdiv_num = request.matchdict["subdiv_num"]
        subdiv_mult = request.matchdict["subdiv_mult"]
        subdiv_pos = request.matchdict["subdiv_pos"]
        self.amendements = (
            DBSession.query(Amendement)
            .filter(
                Amendement.chambre == self.lecture.chambre,
                Amendement.session == self.lecture.session,
                Amendement.num_texte == self.lecture.num_texte,
                Amendement.organe == self.lecture.organe,
                Amendement.subdiv_type == subdiv_type,
                Amendement.subdiv_num == subdiv_num,
                Amendement.subdiv_mult == subdiv_mult,
                Amendement.subdiv_pos == subdiv_pos,
            )
            .all()
        )
        if not self.amendements:
            raise HTTPBadRequest

    @view_config(request_method="GET", renderer="article_edit.html")
    def get(self) -> dict:
        return {"lecture": self.lecture, "amendement": self.amendements[0]}

    @view_config(request_method="POST")
    def post(self) -> Response:
        subdiv_titre = self.request.POST["subdiv_titre"]
        for amendement in self.amendements:
            amendement.subdiv_titre = subdiv_titre
        self.request.session.flash(("success", "Titre mis à jour avec succès."))
        resource = self.request.root["lectures"][amendement.url_key]
        return HTTPFound(location=self.request.resource_url(resource, "amendements"))
