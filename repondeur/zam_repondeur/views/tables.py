from typing import List, Optional

from pyramid.httpexceptions import HTTPForbidden, HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, Amendement, User, UserTable
from zam_repondeur.models.events.amendement import AmendementTransfere
from zam_repondeur.resources import TableResource


@view_defaults(context=TableResource)
class TableView:
    def __init__(self, context: TableResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.table = context.model()
        self.owner = self.table.user
        self.lecture = context.lecture_resource.model()

    @view_config(request_method="GET", renderer="table_detail.html")
    def get(self) -> dict:
        return {
            "lecture": self.lecture,
            "lecture_resource": self.context.lecture_resource,
            "current_tab": "table",
            "table": self.table,
            "amendements": self.table.amendements,
            "is_owner": self.owner.email == self.request.user.email,
            "table_url": self.request.resource_url(
                self.context.parent[self.request.user.email]
            ),
            "index_url": self.request.resource_url(
                self.context.lecture_resource["amendements"]
            ),
            "check_url": self.request.resource_path(self.context, "check"),
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        """
        Transfer amendement(s) from this table to another one, or back to the index
        """
        nums: List[int] = self.request.POST.getall("nums")
        if "submit-index" in self.request.POST:
            target = ""
        elif "submit-table" in self.request.POST:
            target = self.request.user.email
        else:
            target = self.request.POST.get("target")
            if not target:
                self.request.session.flash(
                    Message(
                        cls="warning", text="Veuillez sélectionner un·e destinataire."
                    )
                )
                return HTTPFound(
                    location=self.request.resource_url(
                        self.context.lecture_resource,
                        "transfer_amendements",
                        query={"nums": nums},
                    )
                )

        target_table: Optional[UserTable] = None
        if target:
            if target == self.request.user.email:
                target_user = self.request.user
            else:
                target_user = DBSession.query(User).filter(User.email == target).one()
            if self.request.team and target_user not in self.request.team.users:
                raise HTTPForbidden("Transfert non autorisé")
            target_table = target_user.table_for(self.lecture)

        amendements = DBSession.query(Amendement).filter(
            Amendement.lecture == self.lecture, Amendement.num.in_(nums)  # type: ignore
        )

        for amendement in amendements:
            old = str(amendement.user_table.user) if amendement.user_table else ""
            new = str(target_table.user) if target_table else ""
            if amendement.user_table is target_table:
                continue
            amendement.user_table = target_table
            amendement.stop_editing()
            AmendementTransfere.create(self.request, amendement, old, new)

        if target != self.request.user.email and self.request.POST.get("from_index"):
            next_location = self.request.resource_url(
                self.context.lecture_resource, "amendements"
            )
        else:
            next_location = self.request.resource_url(
                self.context.parent, self.owner.email
            )
        return HTTPFound(location=next_location)


@view_config(context=TableResource, name="check", renderer="json")
def table_check(context: TableResource, request: Request) -> dict:
    table = context.model()
    amendements_as_string = request.GET["current"]
    updated = table.amendements_as_string
    if amendements_as_string != updated:
        return {"updated": updated}
    else:
        return {}
