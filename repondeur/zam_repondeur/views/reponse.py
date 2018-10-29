from datetime import datetime

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.clean import clean_html
from zam_repondeur.decorator import reify
from zam_repondeur.message import Message
from zam_repondeur.models import AVIS
from zam_repondeur.resources import AmendementResource
from zam_repondeur.utils import add_url_fragment, add_url_params


@view_defaults(context=AmendementResource, name="reponse", renderer="reponse_edit.html")
class ReponseEdit:
    def __init__(self, context: AmendementResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.amendement = context.model()
        self.lecture = self.amendement.lecture

    @view_config(request_method="GET")
    def get(self) -> dict:
        return {
            "lecture": self.lecture,
            "amendement": self.amendement,
            "avis": AVIS,
            "back_url": self.back_url,
            "submit_url": self.submit_url,
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        now = datetime.utcnow()
        avis = self.request.POST.get("avis", "")
        observations = clean_html(self.request.POST.get("observations", ""))
        reponse = clean_html(self.request.POST.get("reponse", ""))
        comments = clean_html(self.request.POST.get("comments", ""))

        if (
            avis != (self.amendement.avis or "")
            or observations != (self.amendement.observations or "")
            or reponse != (self.amendement.reponse or "")
            or comments != (self.amendement.comments or "")
        ):
            self.amendement.modified_at = now
            self.lecture.modified_at = now

        self.amendement.avis = avis
        self.amendement.observations = observations
        self.amendement.reponse = reponse
        self.amendement.comments = comments
        self.request.session.flash(
            Message(cls="success", text="Les modifications ont bien été enregistrées.")
        )
        self.request.session["highlighted_amdt"] = self.amendement.slug
        return HTTPFound(location=self.back_url)

    @reify
    def back_url(self) -> str:
        url: str = self.request.GET.get("back")
        if url is None or not url.startswith("/"):
            url = self.request.resource_url(self.context.parent)
        return add_url_fragment(url, self.amendement.slug)

    @property
    def submit_url(self) -> str:
        return add_url_params(self.request.path, back=self.back_url)
