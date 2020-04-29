from datetime import date, datetime

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.message import Message
from zam_repondeur.models import Chambre, DBSession, User
from zam_repondeur.visam.models import Organisation, UserMembership
from zam_repondeur.visam.models.events.membership import (
    MembershipAdded,
    MembershipRemoved,
)
from zam_repondeur.visam.resources import MembersCollection


class MembersCollectionBase:
    def __init__(self, context: MembersCollection, request: Request) -> None:
        self.context = context
        self.request = request


@view_defaults(context=MembersCollection, permission="manage")
class MembersList(MembersCollectionBase):
    @view_config(request_method="GET", renderer="members_list.html")
    def get(self) -> dict:
        users = self.context.models()
        last_event = self.context.events().first()
        if last_event:
            last_event_datetime = last_event.created_at
            last_event_timestamp = (
                last_event_datetime - datetime(1970, 1, 1)
            ).total_seconds()
        else:
            last_event_datetime = None
            last_event_timestamp = None
        organisations = [
            org for org in DBSession.query(Organisation) if not org.is_gouvernement
        ]
        return {
            "users": users,
            "chambres": [Chambre.CCFP, Chambre.CSFPE],
            "organisations": organisations,
            "current_tab": "members",
            "last_event_datetime": last_event_datetime,
            "last_event_timestamp": last_event_timestamp,
        }


@view_defaults(context=MembersCollection, permission="manage")
class MembersDelete(MembersCollectionBase):
    @view_config(request_method="POST")
    def post(self) -> Response:
        user_pk = self.request.POST["user_pk"]
        chambre_name = self.request.POST["chambre_name"]
        organisation_name = self.request.POST["organisation_name"]

        user = DBSession.query(User).filter_by(pk=user_pk).first()
        chambre = Chambre.from_string(chambre_name)
        organisation = (
            DBSession.query(Organisation).filter_by(name=organisation_name).first()
        )

        membership = (
            DBSession.query(UserMembership)
            .filter(
                UserMembership.user_pk == user.pk,
                UserMembership.chambre == chambre,
                UserMembership.organisation == organisation,
            )
            .first()
        )
        MembershipRemoved.create(membership=membership, request=self.request)
        self.request.session.flash(
            Message(
                cls="success",
                text=(
                    f"Membre {user} - {organisation} retiré du "
                    f"{chambre.value} avec succès."
                ),
            )
        )
        return HTTPFound(location=self.request.resource_url(self.context))


@view_defaults(context=MembersCollection, name="add", permission="manage")
class MembersAddForm(MembersCollectionBase):
    @view_config(request_method="POST")
    def post(self) -> Response:
        user_pk = self.request.POST["user_pk"]
        chambre_name = self.request.POST["chambre_name"]
        organisation_name = self.request.POST["organisation_name"]

        user = DBSession.query(User).filter_by(pk=user_pk).first()
        chambre = Chambre.from_string(chambre_name)
        organisation = (
            DBSession.query(Organisation).filter_by(name=organisation_name).first()
        )

        membership = (
            DBSession.query(UserMembership)
            .filter(
                UserMembership.user_pk == user.pk,
                UserMembership.chambre == chambre,
                UserMembership.organisation == organisation,
            )
            .first()
        )
        if membership:
            self.request.session.flash(
                Message(
                    cls="warning",
                    text=(
                        f"Cet·te utilisateur·ice : {user} - {organisation} "
                        f"est déjà membre du {chambre.value}."
                    ),
                )
            )
            return HTTPFound(location=self.request.resource_url(self.context))

        MembershipAdded.create(
            target_user=user,
            target_chambre=chambre,
            target_organisation=organisation,
            comment=None,
            request=self.request,
        )

        self.request.session.flash(
            Message(
                cls="success",
                text=(
                    f"Membre {user} - {organisation} ajouté au "
                    f"{chambre.value} avec succès."
                ),
            )
        )
        return HTTPFound(location=self.request.resource_url(self.context))


@view_config(
    context=MembersCollection,
    permission="manage",
    name="journal",
    renderer="members_journal.html",
)
def members_journal(context: MembersCollection, request: Request) -> Response:
    events = context.events().all()
    return {"events": events, "today": date.today(), "current_tab": "members"}
