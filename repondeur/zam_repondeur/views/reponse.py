from datetime import datetime

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.clean import clean_html
from zam_repondeur.message import Message
from zam_repondeur.models import AVIS
from zam_repondeur.models.visionneuse import build_tree
from zam_repondeur.resources import (
    AmendementCollection,
    AmendementResource,
    LectureResource,
)


@view_config(context=LectureResource, name="reponses", renderer="visionneuse.html")
def list_reponses(context: LectureResource, request: Request) -> Response:
    lecture = context.model()
    amendements = lecture.amendements
    articles = build_tree(amendements)
    check_url = request.resource_path(context, "check")
    return {
        "dossier_legislatif": lecture.dossier_legislatif,
        "lecture": str(lecture),
        "articles": articles,
        "timestamp": lecture.modified_at_timestamp,
        "check_url": check_url,
    }


@view_defaults(context=AmendementResource, name="reponse", renderer="reponse_edit.html")
class ReponseEdit:
    def __init__(self, context: AmendementResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.amendement = context.model()
        self.lecture = context.lecture_resource.model()

    @view_config(request_method="GET")
    def get(self) -> dict:
        return {"lecture": self.lecture, "amendement": self.amendement, "avis": AVIS}

    @view_config(request_method="POST")
    def post(self) -> Response:
        self.amendement.avis = self.request.POST["avis"]
        self.amendement.observations = clean_html(self.request.POST["observations"])
        self.amendement.reponse = clean_html(self.request.POST["reponse"])
        self.amendement.comments = clean_html(self.request.POST["comments"])
        self.lecture.modified_at = datetime.utcnow()
        self.request.session.flash(
            Message(cls="success", text="Les modifications ont bien été enregistrées.")
        )

        collection: AmendementCollection = self.context.parent
        return HTTPFound(location=self.request.resource_url(collection))
