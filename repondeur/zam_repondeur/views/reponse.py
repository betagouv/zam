import base64

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from sqlalchemy.sql.expression import case

from zam_aspirateur.amendements.writer import GROUPS_COLORS

from zam_visionneuse.models import Amendement, Article, Articles, Reponse, Reponses
from zam_visionneuse.templates import render

from zam_repondeur.models import (
    DBSession,
    Amendement as AmendementModel,
    CHAMBRES,
    AVIS,
    Lecture,
)


@view_config(route_name="list_reponses")
def list_reponses(request: Request) -> dict:
    lecture = Lecture.get(
        chambre=request.matchdict["chambre"],
        session=request.matchdict["session"],
        num_texte=int(request.matchdict["num_texte"]),
    )
    if lecture is None:
        raise HTTPNotFound

    amendements = (
        DBSession.query(AmendementModel)
        .filter(
            AmendementModel.chambre == lecture.chambre,
            AmendementModel.session == lecture.session,
            AmendementModel.num_texte == lecture.num_texte,
        )
        .order_by(
            case([(AmendementModel.position.is_(None), 1)], else_=0),
            AmendementModel.position,
            AmendementModel.num,
        )
        .all()
    )
    reponses = Reponses()
    articles = Articles()
    for amendement in amendements:
        if amendement.avis:
            if amendement.subdiv_num in articles:
                article = articles[amendement.subdiv_num]
            else:
                article = Article(
                    pk=amendement.subdiv_num,
                    id=amendement.subdiv_num,
                    titre=amendement.subdiv_type,
                )
                articles[article.pk] = article
            amd = Amendement(
                pk=amendement.num,
                id=amendement.num,
                groupe={
                    "libelle": amendement.groupe,
                    "couleur": GROUPS_COLORS.get(amendement.groupe, "#ffffff"),
                },
                article=article,
                auteur=amendement.auteur,
                dispositif=amendement.dispositif,
                objet=amendement.objet,
                resume=amendement.resume,
            )
            if amendement.reponse:
                reponse = Reponse(
                    pk=base64.b64encode(amendement.reponse.encode()).decode(),
                    avis=amendement.avis,
                    presentation=amendement.observations,
                    content=amendement.reponse,
                    article=article,
                    amendements=[amd],
                )
                reponses[reponse.pk] = reponse

    return Response(render(title=lecture, articles=articles, reponses=reponses))


@view_defaults(route_name="reponse_edit", renderer="reponse_edit.html")
class ReponseEdit:
    def __init__(self, request: Request) -> None:
        self.request = request

        chambre = request.matchdict["chambre"]
        session = request.matchdict["session"]
        num_texte = int(request.matchdict["num_texte"])
        num = int(request.matchdict["num"])
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
