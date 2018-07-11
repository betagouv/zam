from datetime import datetime

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from sqlalchemy.sql.expression import case

from zam_repondeur.clean import clean_html
from zam_repondeur.models import DBSession, Amendement as AmendementModel, AVIS, Lecture
from zam_repondeur.models.visionneuse import build_tree


@view_config(route_name="list_reponses", renderer="visionneuse.html")
def list_reponses(request: Request) -> Response:
    lecture = Lecture.get(
        chambre=request.matchdict["chambre"],
        session=request.matchdict["session"],
        num_texte=int(request.matchdict["num_texte"]),
        organe=request.matchdict["organe"],
    )
    if lecture is None:
        raise HTTPNotFound

    amendements = (
        DBSession.query(AmendementModel)
        .filter(
            AmendementModel.chambre == lecture.chambre,
            AmendementModel.session == lecture.session,
            AmendementModel.num_texte == lecture.num_texte,
            AmendementModel.organe == lecture.organe,
        )
        .order_by(
            case([(AmendementModel.position.is_(None), 1)], else_=0),  # type: ignore
            AmendementModel.position,
            AmendementModel.num,
        )
        .all()
    )
    articles = build_tree(amendements)
    check_url = request.route_path(
        "lecture_check",
        chambre=lecture.chambre,
        session=lecture.session,
        num_texte=lecture.num_texte,
        organe=lecture.organe,
    )
    return {
        "title": str(lecture),
        "articles": articles,
        "timestamp": lecture.modified_at_timestamp,
        "check_url": check_url,
    }


@view_defaults(route_name="reponse_edit", renderer="reponse_edit.html")
class ReponseEdit:
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

    @view_config(request_method="GET")
    def get(self) -> dict:
        return {"lecture": self.lecture, "amendement": self.amendement, "avis": AVIS}

    @view_config(request_method="POST")
    def post(self) -> Response:
        self.amendement.avis = self.request.POST["avis"]
        self.amendement.observations = clean_html(self.request.POST["observations"])
        self.amendement.reponse = clean_html(self.request.POST["reponse"])
        self.lecture.modified_at = datetime.utcnow()
        return HTTPFound(
            location=self.request.route_url(
                "list_amendements",
                chambre=self.amendement.chambre,
                session=self.amendement.session,
                num_texte=self.amendement.num_texte,
                organe=self.amendement.organe,
            )
        )
