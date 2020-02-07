from datetime import date

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from sqlalchemy.orm import subqueryload

from zam_repondeur.message import Message
from zam_repondeur.models import DBSession
from zam_repondeur.models.events.dossier import DossierDesactive
from zam_repondeur.resources import DossierResource
from zam_repondeur.tasks.fetch import update_dossier


class DossierViewBase:
    def __init__(self, context: DossierResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.dossier = context.dossier


@view_defaults(context=DossierResource)
class DossierView(DossierViewBase):
    @view_config(request_method="GET", renderer="dossier_item.html")
    def get(self) -> Response:
        return {
            "dossier": self.dossier,
            "dossier_resource": self.context,
            "current_tab": "dossier",
            "lectures": sorted(self.dossier.lectures),
            "allowed_to_delete": self.request.has_permission("delete", self.context),
        }

    @view_config(request_method="POST", permission="delete")
    def post(self) -> Response:
        DBSession.delete(self.dossier.team)
        for lecture in self.dossier.lectures:
            DBSession.delete(lecture)
        DBSession.flush()
        DossierDesactive.create(dossier=self.dossier, request=self.request)
        self.request.session.flash(
            Message(cls="success", text="Dossier supprimé avec succès.")
        )
        return HTTPFound(location=self.request.resource_url(self.context.parent))


@view_config(context=DossierResource, name="journal", renderer="dossier_journal.html")
def dossier_journal(context: DossierResource, request: Request) -> Response:
    dossier = context.model(
        subqueryload("events").joinedload("user").load_only("email", "name")
    )
    allowed_to_refresh = request.has_permission("refresh_dossier", context)
    return {
        "dossier": dossier,
        "dossier_resource": context,
        "today": date.today(),
        "current_tab": "journal",
        "allowed_to_refresh": allowed_to_refresh,
    }


@view_config(
    context=DossierResource, name="manual_refresh", permission="refresh_dossier"
)
def manual_refresh(context: DossierResource, request: Request) -> Response:
    dossier = context.dossier
    update_dossier(dossier.pk, force=True)
    request.session.flash(
        Message(cls="success", text="Rafraîchissement des lectures en cours.")
    )
    return HTTPFound(location=request.resource_url(context))
