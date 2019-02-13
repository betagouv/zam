from typing import List, Optional

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.models import DBSession, Amendement, User, UserTable
from zam_repondeur.models.events.amendement import AmendementTransfere
from zam_repondeur.resources import TableResource


@view_defaults(context=TableResource)
class TableView:
    def __init__(self, context: TableResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.lecture = context.lecture_resource.model()
        self.owner = context.owner

    @view_config(request_method="GET", renderer="table_detail.html")
    def get(self) -> dict:
        return {
            "lecture": self.lecture,
            "amendements": self.context.amendements(),
            "is_owner": self.owner.email == self.request.user.email,
            "owner": self.owner,
            "users": DBSession.query(User).filter(
                User.email != self.request.user.email, User.email != self.owner.email
            ),
            "table_url": self.request.resource_url(
                self.context.parent[self.request.user.email]
            ),
            "index_url": self.request.resource_url(
                self.context.lecture_resource["amendements"]
            ),
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        """
        Transfer amendement(s) from this table to another one, or back to the index
        """
        nums: List[int] = self.request.POST.getall("nums")
        target: str = self.request.POST.get("target")

        target_table: Optional[UserTable] = None
        if target:
            target_user: User = DBSession.query(User).filter(User.email == target).one()
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
            AmendementTransfere.create(self.request, amendement, old, new)
        return HTTPFound(
            location=self.request.resource_url(self.context.parent, self.owner.email)
        )
