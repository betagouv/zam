from datetime import date
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
    CommentsAmendementModifie,
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
        self.my_table_resource = self.context.lecture_resource["tables"][
            self.request.user.email
        ]
        self.is_on_my_table = (
            self.amendement.user_table
            and self.amendement.user_table.user == self.request.user
        )

    @view_config(request_method="GET")
    def get(self) -> dict:
        check_url = self.request.resource_path(self.my_table_resource, "check")
        return {
            "amendement": self.amendement,
            "avis": AVIS,
            "table": self.amendement.user_table,
            "is_on_my_table": self.is_on_my_table,
            "back_url": self.back_url,
            "submit_url": self.submit_url,
            "check_url": check_url,
            "my_table_url": self.my_table_url,
            "transfer_url": self.request.resource_url(
                self.context.parent.parent,
                "transfer_amendements",
                query={"nums": self.amendement.num, "from_index": 1},
            ),
            "reponses": self.amendement.article.grouped_displayable_amendements(),
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        avis = self.request.POST.get("avis", "")
        objet = clean_html(self.request.POST.get("objet", ""))
        reponse = clean_html(self.request.POST.get("reponse", ""))
        comments = clean_html(self.request.POST.get("comments", ""))

        avis_changed = avis != (self.amendement.user_content.avis or "")
        objet_changed = objet != (self.amendement.user_content.objet or "")
        reponse_changed = reponse != (self.amendement.user_content.reponse or "")
        comments_changed = comments != (self.amendement.user_content.comments or "")

        if not self.is_on_my_table:
            message = (
                "Les modifications n’ont PAS été enregistrées "
                "car l’amendement n’est plus sur votre table."
            )
            if self.amendement.user_table:
                message += (
                    f" Il est actuellement sur la table de "
                    f"{self.amendement.user_table.user}."
                )
            self.request.session.flash(Message(cls="danger", text=message))
            return HTTPFound(location=self.my_table_url)

        if avis_changed:
            AvisAmendementModifie.create(self.request, self.amendement, avis)

        if objet_changed:
            ObjetAmendementModifie.create(self.request, self.amendement, objet)

        if reponse_changed:
            ReponseAmendementModifiee.create(self.request, self.amendement, reponse)

        if comments_changed:
            CommentsAmendementModifie.create(self.request, self.amendement, comments)

        self.amendement.stop_editing()

        self.request.session.flash(
            Message(cls="success", text="Les modifications ont bien été enregistrées.")
        )
        if "save-and-transfer" in self.request.POST:
            return HTTPFound(
                location=self.request.resource_url(
                    self.context.parent.parent,
                    "transfer_amendements",
                    query={"nums": self.amendement.num, "from_save": 1},
                )
            )
        else:
            self.request.session["highlighted_amdt"] = self.amendement.slug
            return HTTPFound(location=self.back_url)

    @reify
    def back_url(self) -> str:
        url: str = self.request.GET.get("back")
        if url is None or not url.startswith("/"):
            url = self.my_table_url
        return add_url_fragment(url, self.amendement.slug)

    @property
    def submit_url(self) -> str:
        return add_url_params(self.request.path, back=self.back_url)

    @property
    def my_table_url(self) -> str:
        return self.request.resource_url(self.my_table_resource)


@view_config(
    context=AmendementResource, name="journal", renderer="amendement_journal.html"
)
def amendement_journal(context: AmendementResource, request: Request) -> Dict[str, Any]:
    return {
        "lecture": context.lecture_resource.model(),
        "amendement": context.model(),
        "today": date.today(),
        "back_url": request.resource_url(context, "amendement_edit"),
    }


@view_config(context=AmendementResource, name="start_editing", renderer="json")
def start_editing(context: AmendementResource, request: Request) -> dict:
    context.model().start_editing()
    return {}


@view_config(context=AmendementResource, name="stop_editing", renderer="json")
def stop_editing(context: AmendementResource, request: Request) -> dict:
    context.model().stop_editing()
    return {}
