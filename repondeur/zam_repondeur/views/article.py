from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.clean import clean_html
from zam_repondeur.models import DBSession, Amendement
from zam_repondeur.resources import ArticleResource


@view_defaults(context=ArticleResource)
class ArticleEdit:
    def __init__(self, context: ArticleResource, request: Request) -> None:
        self.context = context
        self.request = request

        self.lecture = context.lecture_resource.model()

        self.amendements = (
            DBSession.query(Amendement)
            .filter(
                Amendement.chambre == self.lecture.chambre,
                Amendement.session == self.lecture.session,
                Amendement.num_texte == self.lecture.num_texte,
                Amendement.organe == self.lecture.organe,
                Amendement.subdiv_type == self.context.subdiv_type,
                Amendement.subdiv_num == self.context.subdiv_num,
                Amendement.subdiv_mult == self.context.subdiv_mult,
                Amendement.subdiv_pos == self.context.subdiv_pos,
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
        subdiv_jaune = clean_html(self.request.POST["subdiv_jaune"])
        for amendement in self.amendements:
            amendement.subdiv_titre = subdiv_titre
            amendement.subdiv_jaune = subdiv_jaune
        self.request.session.flash(("success", "Article mis à jour avec succès."))
        resource = self.context.lecture_resource["amendements"]
        return HTTPFound(location=self.request.resource_url(resource))
