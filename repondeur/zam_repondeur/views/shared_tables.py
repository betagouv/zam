from slugify import slugify
from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, SharedTable, get_one_or_create
from zam_repondeur.models.events.lecture import (
    SharedTableCreee,
    SharedTableRenommee,
    SharedTableSupprimee,
)
from zam_repondeur.resources import (
    SharedTableCollection,
    SharedTableResource,
    SharedTableDeleteResource,
)


@view_defaults(context=SharedTableCollection, name="add")
class SharedTableCollectionView:
    def __init__(self, context: SharedTableCollection, request: Request) -> None:
        self.context = context
        self.request = request
        self.lecture = context.lecture_resource.model()

    @view_config(request_method="GET", renderer="shared_table_detail.html")
    def get(self) -> dict:
        return {
            "lecture": self.lecture,
            "lecture_resource": self.context.lecture_resource,
            "dossier_resource": self.context.lecture_resource.dossier_resource,
            "current_tab": "options",
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        titre: str = self.request.POST.get("titre")
        table, created = get_one_or_create(
            SharedTable, titre=titre, lecture=self.lecture
        )
        if created:
            SharedTableCreee.create(
                request=self.request, lecture=self.lecture, titre=titre
            )
            self.request.session.flash(
                Message(
                    cls="success", text=f"Boîte « {table.titre} » créée avec succès."
                )
            )
        else:
            self.request.session.flash(
                Message(cls="warning", text=f"La boîte « {table.titre} » existe déjà…")
            )
        return HTTPFound(
            location=self.request.resource_url(
                self.context.lecture_resource, "options", anchor="shared-tables"
            )
        )


@view_defaults(context=SharedTableResource)
class SharedTableResourceView:
    def __init__(self, context: SharedTableResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.lecture = context.lecture_resource.model()
        self.shared_table = self.context.model()

    @view_config(request_method="GET", renderer="shared_table_detail.html")
    def get(self) -> dict:
        return {
            "lecture": self.lecture,
            "lecture_resource": self.context.lecture_resource,
            "dossier_resource": self.context.lecture_resource.dossier_resource,
            "shared_table": self.shared_table,
            "current_tab": "options",
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        old_titre = self.shared_table.titre
        titre: str = self.request.POST.get("titre")
        self.shared_table.titre = titre
        self.shared_table.slug = slugify(titre)
        SharedTableRenommee.create(
            request=self.request,
            lecture=self.lecture,
            old_titre=old_titre,
            new_titre=titre,
        )
        self.request.session.flash(
            Message(cls="success", text=f"Boîte « {titre} » sauvegardée avec succès.")
        )
        return HTTPFound(
            location=self.request.resource_url(
                self.context.lecture_resource, "options", anchor="shared-tables"
            )
        )


@view_defaults(context=SharedTableDeleteResource)
class SharedTableResourceDeleteView:
    def __init__(self, context: SharedTableResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.lecture = context.lecture_resource.model()
        self.shared_table = self.context.model()

    @view_config(request_method="GET", renderer="shared_table_delete.html")
    def get(self) -> dict:
        return {
            "lecture": self.lecture,
            "lecture_resource": self.context.lecture_resource,
            "dossier_resource": self.context.lecture_resource.dossier_resource,
            "shared_table": self.shared_table,
            "current_tab": "options",
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        titre = self.shared_table.titre
        DBSession.delete(self.shared_table)
        SharedTableSupprimee.create(
            request=self.request, lecture=self.lecture, titre=titre
        )
        self.request.session.flash(
            Message(cls="success", text=f"Boîte « {titre} » supprimée avec succès.")
        )
        return HTTPFound(
            location=self.request.resource_url(
                self.context.lecture_resource, "options", anchor="shared-tables"
            )
        )
