from datetime import date, datetime

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.message import Message
from zam_repondeur.models import AllowedEmailPattern, DBSession, User
from zam_repondeur.models.events.whitelist import WhitelistAdd, WhitelistRemove
from zam_repondeur.resources import WhitelistCollection


class WhitelistCollectionBase:
    def __init__(self, context: WhitelistCollection, request: Request) -> None:
        self.context = context
        self.request = request


@view_defaults(context=WhitelistCollection, permission="manage")
class WhitelistList(WhitelistCollectionBase):
    @view_config(request_method="GET", renderer="whitelist_list.html")
    def get(self) -> dict:
        email_patterns = self.context.models()
        last_event = self.context.events().first()
        if last_event:
            last_event_datetime = last_event.created_at
            last_event_timestamp = (
                last_event_datetime - datetime(1970, 1, 1)
            ).total_seconds()
        else:
            last_event_datetime = None
            last_event_timestamp = None
        return {
            "email_patterns": email_patterns,
            "current_tab": "whitelist",
            "last_event_datetime": last_event_datetime,
            "last_event_timestamp": last_event_timestamp,
        }


@view_defaults(context=WhitelistCollection, permission="manage")
class WhitelistDelete(WhitelistCollectionBase):
    @view_config(request_method="POST")
    def post(self) -> Response:
        email_pattern_pk = self.request.POST["pk"]
        allowed_email_pattern = (
            DBSession.query(AllowedEmailPattern).filter_by(pk=email_pattern_pk).first()
        )
        WhitelistRemove.create(
            allowed_email_pattern=allowed_email_pattern, request=self.request
        )
        self.request.session.flash(
            Message(
                cls="success",
                text=("Adresse de courriel ou modèle supprimé(e) avec succès."),
            )
        )
        return HTTPFound(location=self.request.resource_url(self.context))


@view_defaults(context=WhitelistCollection, name="add", permission="manage")
class WhitelistAddForm(WhitelistCollectionBase):
    @view_config(request_method="GET", renderer="whitelist_add.html")
    def get(self) -> dict:
        return {"current_tab": "whitelist"}

    @view_config(request_method="POST")
    def post(self) -> Response:
        email_pattern = self.request.POST["email_pattern"] or ""

        if not email_pattern:
            self.request.session.flash(
                Message(cls="error", text="Veuillez saisir un courriel ou modèle.")
            )
            return HTTPFound(location=self.request.resource_url(self.context))

        allowed_email_pattern = (
            DBSession.query(AllowedEmailPattern)
            .filter_by(pattern=email_pattern)
            .first()
        )

        if allowed_email_pattern:
            self.request.session.flash(
                Message(cls="warning", text="Cette adresse de courriel existe déjà.")
            )
            return HTTPFound(location=self.request.resource_url(self.context))

        if User.email_is_allowed(email_pattern):
            self.request.session.flash(
                Message(
                    cls="warning", text="Cette adresse de courriel est déjà acceptée."
                )
            )
            return HTTPFound(location=self.request.resource_url(self.context))

        WhitelistAdd.create(
            email_pattern=email_pattern, comment=None, request=self.request
        )

        self.request.session.flash(
            Message(
                cls="success",
                text=("Adresse de courriel ou modèle créé(e) avec succès."),
            )
        )
        return HTTPFound(location=self.request.resource_url(self.context))


@view_config(
    context=WhitelistCollection,
    permission="manage",
    name="journal",
    renderer="whitelist_journal.html",
)
def whitelist_journal(context: WhitelistCollection, request: Request) -> Response:
    events = context.events().all()
    return {"events": events, "today": date.today(), "current_tab": "whitelist"}
