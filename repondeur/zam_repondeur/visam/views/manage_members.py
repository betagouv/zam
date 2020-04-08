from datetime import date, datetime

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.message import Message
from zam_repondeur.models import Chambre, DBSession, User
from zam_repondeur.visam.models import UserChambreMembership
from zam_repondeur.visam.models.events.members import MembersAdd, MembersRemove
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
        return {
            "users": users,
            "chambres": [Chambre.CCFP, Chambre.CSFPE],
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

        user = DBSession.query(User).filter_by(pk=user_pk).first()
        chambre = Chambre.from_string(chambre_name)

        membership = (
            DBSession.query(UserChambreMembership)
            .filter(
                UserChambreMembership.user_pk == user.pk,
                UserChambreMembership.chambre == chambre,
            )
            .first()
        )
        MembersRemove.create(membership=membership, request=self.request)
        self.request.session.flash(
            Message(
                cls="success",
                text=f"Membre {user} retiré du {chambre.value} avec succès.",
            )
        )
        return HTTPFound(location=self.request.resource_url(self.context))


@view_defaults(context=MembersCollection, name="add", permission="manage")
class MembersAddForm(MembersCollectionBase):
    @view_config(request_method="POST")
    def post(self) -> Response:
        user_pk = self.request.POST["user_pk"]
        chambre_name = self.request.POST["chambre_name"]

        user = DBSession.query(User).filter_by(pk=user_pk).first()
        chambre = Chambre.from_string(chambre_name)

        membership = (
            DBSession.query(UserChambreMembership)
            .filter(
                UserChambreMembership.user_pk == user.pk,
                UserChambreMembership.chambre == chambre,
            )
            .first()
        )
        if membership:
            self.request.session.flash(
                Message(
                    cls="warning",
                    text=(
                        f"Cet·te utilisateur·ice ({user}) "
                        f"est déjà membre du {chambre.value}."
                    ),
                )
            )
            return HTTPFound(location=self.request.resource_url(self.context))

        MembersAdd.create(
            target_user=user,
            target_chambre=chambre,
            comment=None,
            request=self.request,
        )

        self.request.session.flash(
            Message(
                cls="success",
                text=f"Membre {user} ajouté au {chambre.value} avec succès.",
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
