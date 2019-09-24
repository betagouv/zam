from datetime import datetime

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, User
from zam_repondeur.resources import AdminsCollection


class AdminsCollectionBase:
    def __init__(self, context: AdminsCollection, request: Request) -> None:
        self.context = context
        self.request = request


@view_defaults(context=AdminsCollection, permission="manage")
class AdminsList(AdminsCollectionBase):
    @view_config(request_method="GET", renderer="admins_list.html")
    def get(self) -> dict:
        admins = self.context.models()
        return {"admins": admins, "current_tab": "admins"}


@view_defaults(context=AdminsCollection, permission="manage")
class AdminsRemove(AdminsCollectionBase):
    @view_config(request_method="POST")
    def post(self) -> Response:
        user_pk = self.request.POST["user_pk"]
        if str(self.request.user.pk) == user_pk:
            message = "Vous ne pouvez pas vous retirer du statut d’administrateur."
            self.request.session.flash(Message(cls="warning", text=message))
            return HTTPFound(location=self.request.resource_url(self.context))
        user = DBSession.query(User).filter_by(pk=user_pk).first()
        user.admin_at = None
        self.request.session.flash(
            Message(
                cls="success", text=("Droits d’administration retirés avec succès.")
            )
        )
        return HTTPFound(location=self.request.resource_url(self.context))


@view_defaults(context=AdminsCollection, name="add", permission="manage")
class AdminsAddForm(AdminsCollectionBase):
    @view_config(request_method="GET", renderer="admins_add.html")
    def get(self) -> dict:
        users = DBSession.query(User).all()
        return {"current_tab": "admins", "users": users}

    @view_config(request_method="POST")
    def post(self) -> Response:
        user_pk = self.request.POST["user_pk"]
        user = DBSession.query(User).filter_by(pk=user_pk).first()
        user.admin_at = datetime.utcnow()
        self.request.session.flash(
            Message(
                cls="success", text=("Droits d’administration ajoutés avec succès.")
            )
        )
        return HTTPFound(location=self.request.resource_url(self.context))
