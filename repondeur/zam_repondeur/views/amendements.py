from datetime import datetime, date
from typing import Any, Dict

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
from zam_repondeur.models.events.amendement import (
    AvisAmendementModifie,
    ObjetAmendementModifie,
    ReponseAmendementModifiee,
)


@view_defaults(
    context=AmendementResource, name="amendement_edit", renderer="amendement_edit.html"
)
class AmendementEdit:
    def __init__(self, context: AmendementResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.amendement = context.model()
        self.lecture = self.amendement.lecture

    @view_config(request_method="GET")
    def get(self) -> dict:
        return {
            "amendement": self.amendement,
            "avis": AVIS,
            "back_url": self.back_url,
            "submit_url": self.submit_url,
            "reponses": self.amendement.article.grouped_displayable_amendements(),
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        now = datetime.utcnow()
        avis = self.request.POST.get("avis", "")
        objet = clean_html(self.request.POST.get("objet", ""))
        reponse = clean_html(self.request.POST.get("reponse", ""))
        comments = clean_html(self.request.POST.get("comments", ""))

        avis_changed = avis != self.amendement.user_content.avis
        objet_changed = objet != (self.amendement.user_content.objet or "")
        reponse_changed = reponse != (self.amendement.user_content.reponse or "")
        comments_changed = comments != (self.amendement.user_content.comments or "")

        if avis_changed or objet_changed or reponse_changed or comments_changed:
            self.amendement.modified_at = now
            self.lecture.modified_at = now

        if avis_changed:
            AvisAmendementModifie.create(self.request, self.amendement, avis)

        if objet_changed:
            ObjetAmendementModifie.create(self.request, self.amendement, objet)

        if reponse_changed:
            ReponseAmendementModifiee.create(self.request, self.amendement, reponse)

        if comments_changed:
            self.amendement.user_content.comments = comments
            # No event for comments change.

        self.request.session.flash(
            Message(cls="success", text="Les modifications ont bien été enregistrées.")
        )
        if "save-and-transfer" in self.request.POST:
            return HTTPFound(
                location=self.request.resource_url(
                    self.context.parent.parent,
                    "transfer_amendements",
                    query={"nums": self.amendement.num},
                )
            )
        else:
            self.request.session["highlighted_amdt"] = self.amendement.slug
            return HTTPFound(location=self.back_url)

    @reify
    def back_url(self) -> str:
        url: str = self.request.GET.get("back")
        if url is None or not url.startswith("/"):
            my_table = self.context.lecture_resource["tables"][self.request.user.email]
            url = self.request.resource_url(my_table)
        return add_url_fragment(url, self.amendement.slug)

    @property
    def submit_url(self) -> str:
        return add_url_params(self.request.path, back=self.back_url)


@view_config(
    context=AmendementResource,
    name="amendement_journal",
    renderer="amendement_journal.html",
)
def article_journal(context: AmendementResource, request: Request) -> Dict[str, Any]:
    return {
        "lecture": context.lecture_resource.model(),
        "amendement": context.model(),
        "today": date.today(),
    }
