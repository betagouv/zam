from typing import List, Optional

from pyramid.httpexceptions import HTTPForbidden, HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from sqlalchemy.orm import joinedload, load_only, subqueryload
from sqlalchemy.orm.exc import NoResultFound

from zam_repondeur.message import Message
from zam_repondeur.models import (
    Amendement,
    Batch,
    DBSession,
    SharedTable,
    User,
    UserTable,
)
from zam_repondeur.models.events.amendement import AmendementTransfere
from zam_repondeur.resources import TableResource


@view_defaults(context=TableResource)
class TableView:
    def __init__(self, context: TableResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.lecture = context.lecture_resource.model(
            subqueryload("amendements")
            .joinedload("user_content")
            .load_only("avis", "objet", "reponse_hash")
        )

    @view_config(request_method="GET", renderer="table_detail.html")
    def get(self) -> dict:
        table = self.context.model(
            subqueryload("amendements_locations").options(
                load_only("amendement_pk"),
                joinedload("amendement").options(
                    load_only(
                        "article_pk",
                        "auteur",
                        "groupe",
                        "id_identique",
                        "lecture_pk",
                        "mission_titre",
                        "num",
                        "parent_pk",
                        "position",
                        "rectif",
                        "sort",
                    ),
                    joinedload("user_content").load_only(
                        "avis", "objet", "reponse_hash"
                    ),
                    joinedload("location").options(
                        load_only("batch_pk"),
                        subqueryload("batch")
                        .joinedload("amendements_locations")
                        .options(
                            load_only("amendement_pk"),
                            joinedload("amendement").load_only("num", "rectif"),
                        ),
                    ),
                    joinedload("article").load_only(
                        "lecture_pk", "type", "num", "mult", "pos"
                    ),
                ),
            )
        )
        return {
            "lecture": self.lecture,
            "lecture_resource": self.context.lecture_resource,
            "dossier_resource": self.context.lecture_resource.dossier_resource,
            "current_tab": "table",
            "table": table,
            "all_amendements": table.amendements,
            "collapsed_amendements": Batch.collapsed_batches(table.amendements),
            "is_owner": table.user.email == self.request.user.email,
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

        target_user_table = self.get_target_user_table(target)
        target_shared_table = self.get_target_shared_table(target)

        amendements = DBSession.query(Amendement).filter(
            Amendement.lecture == self.lecture, Amendement.num.in_(nums)  # type: ignore
        )

        for amendement in Batch.expanded_batches(amendements):
            old = amendement.table_name_with_email
            if target_shared_table:
                if target and amendement.location.shared_table is target_shared_table:
                    continue
                new = target_shared_table.titre
                amendement.location.shared_table = target_shared_table
                amendement.location.user_table = None
            else:
                if target and amendement.location.user_table is target_user_table:
                    continue
                new = str(target_user_table.user) if target_user_table else ""
                amendement.location.user_table = target_user_table
                amendement.location.shared_table = None
            amendement.stop_editing()
            AmendementTransfere.create(
                amendement=amendement,
                old_value=old,
                new_value=new,
                request=self.request,
            )

        if target != self.request.user.email and self.request.POST.get("from_index"):
            amendements_collection = self.context.lecture_resource["amendements"]
            next_location = self.request.resource_url(amendements_collection)
        else:
            table = self.context.model()
            table_resource = self.context.parent[table.user.email]
            next_location = self.request.resource_url(table_resource)
        return HTTPFound(location=next_location)

    def get_target_user_table(self, target: str) -> Optional[UserTable]:
        if not target or "@" not in target:
            return None
        if target == self.request.user.email:
            target_user = self.request.user
        else:
            target_user = DBSession.query(User).filter(User.email == target).one()
        if (
            target_user
            not in self.context.lecture_resource.dossier_resource.dossier.team.users
        ):
            raise HTTPForbidden("Transfert non autorisé")
        return target_user.table_for(self.lecture)

    def get_target_shared_table(self, target: str) -> Optional[SharedTable]:
        if not target or "@" in target:
            return None
        try:
            result: Optional[SharedTable] = (
                DBSession.query(SharedTable)
                .filter(SharedTable.slug == target, SharedTable.lecture == self.lecture)
                .one()
            )
        except NoResultFound:
            raise HTTPForbidden("Boîte non disponible.")
        return result


@view_config(context=TableResource, name="check", renderer="json")
def table_check(context: TableResource, request: Request) -> dict:
    table = context.model()
    amendements_as_string = request.GET["current"]
    updated = table.amendements_as_string
    if amendements_as_string != updated:
        return {"updated": updated}
    else:
        return {}
