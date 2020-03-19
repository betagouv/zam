from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from sqlalchemy.orm import joinedload

from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, Dossier, Team, User
from zam_repondeur.models.events.dossier import DossierActive
from zam_repondeur.resources import DossierCollection
from zam_repondeur.tasks.fetch import create_missing_lectures


class DossierCollectionBase:
    def __init__(self, context: DossierCollection, request: Request) -> None:
        self.context = context
        self.request = request
        self.dossiers = context.models(joinedload("team"))


@view_defaults(context=DossierCollection)
class DossierList(DossierCollectionBase):
    @view_config(request_method="GET", renderer="dossiers_list.html")
    def get(self) -> dict:
        my_dossiers = [
            dossier
            for dossier in self.dossiers
            if dossier.team
            and (self.request.user.is_admin or dossier.team in self.request.user.teams)
        ]
        return {
            "dossiers": my_dossiers,
            "allowed_to_activate": self.request.has_permission(
                "activate", self.context
            ),
            "current_tab": "dossiers",
        }


@view_defaults(context=DossierCollection, name="add", permission="activate")
class DossierAddForm(DossierCollectionBase):
    @view_config(request_method="GET", renderer="dossiers_add.html")
    def get(self) -> dict:
        available_dossiers = [dossier for dossier in self.dossiers if not dossier.team]
        return {"available_dossiers": available_dossiers, "current_tab": "dossiers"}

    @view_config(request_method="POST")
    def post(self) -> Response:
        dossier_slug = self._get_dossier_slug()

        if not dossier_slug:
            self.request.session.flash(
                Message(cls="error", text="Ce dossier n’existe pas.")
            )
            return HTTPFound(location=self.request.resource_url(self.context))

        dossier = Dossier.get(slug=dossier_slug)

        if dossier is None:
            self.request.session.flash(
                Message(cls="error", text="Ce dossier n’existe pas.")
            )
            return HTTPFound(location=self.request.resource_url(self.context))

        if dossier.team:
            self.request.session.flash(
                Message(cls="warning", text="Ce dossier appartient à une autre équipe…")
            )
            return HTTPFound(location=self.request.resource_url(self.context))

        team = Team.create(name=dossier.slug)
        dossier.team = team
        for admin in DBSession.query(User).filter(
            User.admin_at.isnot(None)  # type: ignore
        ):
            admin.teams.append(team)

        # Enqueue task to asynchronously add the lectures
        create_missing_lectures(dossier_pk=dossier.pk, user_pk=self.request.user.pk)

        DossierActive.create(dossier=dossier, request=self.request)

        self.request.session.flash(
            Message(
                cls="success",
                text="Dossier créé avec succès, lectures en cours de création.",
            )
        )
        return HTTPFound(
            location=self.request.resource_url(self.context[dossier.url_key])
        )

    def _get_dossier_slug(self) -> str:
        try:
            dossier_slug = self.request.POST["dossier"] or ""
        except KeyError:
            raise HTTPBadRequest
        return dossier_slug
