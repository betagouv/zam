import bleach
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from sqlalchemy.sql.expression import case

from zam_repondeur.models import (
    DBSession,
    Amendement as AmendementModel,
    CHAMBRES,
    AVIS,
    Lecture,
)
from zam_repondeur.models.visionneuse import build_tree


ALLOWED_TAGS = ["p", "ul", "li", "b", "i", "strong", "em"]


def clean_html(text: str) -> str:
    cleaned: str = bleach.clean(text, strip=True, tags=ALLOWED_TAGS)
    return cleaned


@view_config(route_name="list_reponses", renderer="visionneuse.html")
def list_reponses(request: Request) -> Response:
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
    articles = build_tree(amendements)
    return {"title": str(lecture), "articles": articles}


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
        self.amendement.observations = clean_html(self.request.POST["observations"])
        self.amendement.reponse = clean_html(self.request.POST["reponse"])
        return HTTPFound(
            location=self.request.route_url(
                "list_amendements",
                chambre=self.amendement.chambre,
                session=self.amendement.session,
                num_texte=self.amendement.num_texte,
            )
        )
