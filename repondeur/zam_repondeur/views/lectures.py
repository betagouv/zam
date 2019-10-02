from datetime import date
from typing import Any, List, Optional

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from sqlalchemy.orm import joinedload
from webob.multidict import MultiDict

from zam_repondeur.message import Message
from zam_repondeur.models import Amendement, Batch, DBSession, SharedTable
from zam_repondeur.models.amendement import Reponse
from zam_repondeur.models.events.amendement import (
    AvisAmendementModifie,
    BatchSet,
    BatchUnset,
    CommentsAmendementModifie,
    ObjetAmendementModifie,
    ReponseAmendementModifiee,
)
from zam_repondeur.resources import LectureResource
from zam_repondeur.tasks.fetch import fetch_amendements, fetch_articles


@view_defaults(
    context=LectureResource, renderer="batch_amendements.html", name="batch_amendements"
)
class BatchAmendements:
    def __init__(self, context: LectureResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.lecture = self.context.model(joinedload("amendements"))

    @view_config(request_method="GET")
    def get(self) -> Any:
        amendements = self.get_amendements_from(self.request.GET)

        self.check_amendements_are_all_on_my_table(amendements)
        self.check_amendements_have_all_same_reponse_or_empty(amendements)
        self.check_amendements_are_all_from_same_article(amendements)
        self.check_amendements_are_all_from_same_mission(amendements)

        return {
            "lecture": self.lecture,
            "lecture_resource": self.context,
            "dossier_resource": self.context.dossier_resource,
            "current_tab": "table",
            "amendements": amendements,
            "back_url": self.my_table_url,
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        # Special case: unbatch (TODO: move to a separate route)
        if len(self.request.POST.getall("nums")) == 1:
            amendement = self.get_amendements_from(self.request.POST)[0]
            BatchUnset.create(amendement=amendement, request=self.request)
            return HTTPFound(location=self.my_table_url)

        amendements = list(
            Batch.expanded_batches(self.get_amendements_from(self.request.POST))
        )

        self.check_amendements_are_all_on_my_table(amendements)
        self.check_amendements_have_all_same_reponse_or_empty(amendements)
        self.check_amendements_are_all_from_same_article(amendements)

        batch = Batch.create()
        shared_reponse: Optional[Reponse] = None
        to_be_updated: List[Amendement] = []
        for amendement in amendements:
            if amendement.batch:
                BatchUnset.create(amendement=amendement, request=self.request)
            BatchSet.create(
                amendement=amendement,
                batch=batch,
                amendements_nums=[amendement.num for amendement in amendements],
                request=self.request,
            )
            reponse = Reponse.from_amendement(amendement)
            if not reponse.is_empty:
                shared_reponse = reponse
            else:
                to_be_updated.append(amendement)

        if shared_reponse is not None and to_be_updated:
            for amendement in to_be_updated:
                if (amendement.user_content.avis or "") != shared_reponse.avis:
                    AvisAmendementModifie.create(
                        amendement=amendement,
                        avis=shared_reponse.avis,
                        request=self.request,
                    )
                if (amendement.user_content.objet or "") != shared_reponse.objet:
                    ObjetAmendementModifie.create(
                        amendement=amendement,
                        objet=shared_reponse.objet,
                        request=self.request,
                    )
                if (amendement.user_content.reponse or "") != shared_reponse.content:
                    ReponseAmendementModifiee.create(
                        amendement=amendement,
                        reponse=shared_reponse.content,
                        request=self.request,
                    )
                if (amendement.user_content.comments or "") != shared_reponse.comments:
                    CommentsAmendementModifie.create(
                        amendement=amendement,
                        comments=shared_reponse.comments,
                        request=self.request,
                    )

        return HTTPFound(location=self.my_table_url)

    @property
    def my_table_url(self) -> str:
        table_resource = self.context["tables"][self.request.user.email]
        return self.request.resource_url(table_resource)

    def get_amendements_from(self, source: MultiDict) -> List[Amendement]:
        return [
            amendement
            for amendement in self.lecture.amendements
            if str(amendement.num) in source.getall("nums")
        ]

    def check_amendements_are_all_on_my_table(
        self, amendements: List[Amendement]
    ) -> None:
        are_all_on_my_table = all(
            amendement.user_table.user == self.request.user
            if amendement.user_table
            else False
            for amendement in amendements
        )
        if are_all_on_my_table:
            return

        message = (
            "Tous les amendements doivent être sur votre table "
            "pour pouvoir les associer."
        )
        self.request.session.flash(Message(cls="danger", text=message))
        raise HTTPFound(location=self.my_table_url)

    def check_amendements_have_all_same_reponse_or_empty(
        self, amendements: List[Amendement]
    ) -> None:
        reponses = (Reponse.from_amendement(amendement) for amendement in amendements)
        non_empty_reponses = (reponse for reponse in reponses if not reponse.is_empty)

        if len(set(non_empty_reponses)) <= 1:  # all the same (1) or all empty (0)
            return

        message = (
            "Tous les amendements doivent avoir les mêmes réponses et commentaires "
            "avant de pouvoir être associés."
        )
        self.request.session.flash(Message(cls="danger", text=message))
        raise HTTPFound(location=self.my_table_url)

    def check_amendements_are_all_from_same_article(
        self, amendements: List[Amendement]
    ) -> None:
        first_article = amendements[0].article
        are_all_from_same_article = all(
            amdt.article == first_article for amdt in amendements
        )
        if are_all_from_same_article:
            return

        message = (
            "Tous les amendements doivent être relatifs au même article "
            "pour pouvoir être associés."
        )
        self.request.session.flash(Message(cls="danger", text=message))
        raise HTTPFound(location=self.my_table_url)

    def check_amendements_are_all_from_same_mission(
        self, amendements: List[Amendement]
    ) -> None:
        first_mission = amendements[0].mission
        are_all_from_same_mission = all(
            amdt.mission is first_mission for amdt in amendements
        )
        if are_all_from_same_mission:
            return

        message = (
            "Tous les amendements doivent être relatifs à la même mission "
            "pour pouvoir être associés."
        )
        self.request.session.flash(Message(cls="danger", text=message))
        raise HTTPFound(location=self.my_table_url)


@view_config(context=LectureResource, name="manual_refresh")
def manual_refresh(context: LectureResource, request: Request) -> Response:
    lecture = context.model()
    fetch_amendements(lecture.pk)
    fetch_articles(lecture.pk)
    request.session.flash(
        Message(
            cls="success",
            text="Rafraichissement des amendements et des articles en cours.",
        )
    )
    amendements_collection = context["amendements"]
    return HTTPFound(location=request.resource_url(amendements_collection))


@view_config(context=LectureResource, name="journal", renderer="lecture_journal.html")
def lecture_journal(context: LectureResource, request: Request) -> Response:
    lecture = context.model()
    return {
        "lecture": lecture,
        "dossier_resource": context.dossier_resource,
        "lecture_resource": context,
        "current_tab": "journal",
        "today": date.today(),
        "settings": request.registry.settings,
    }


@view_config(context=LectureResource, name="options", renderer="lecture_options.html")
def lecture_options(context: LectureResource, request: Request) -> Response:
    lecture = context.model()
    shared_tables = DBSession.query(SharedTable).filter(SharedTable.lecture == lecture)
    return {
        "lecture": lecture,
        "dossier_resource": context.dossier_resource,
        "lecture_resource": context,
        "current_tab": "options",
        "shared_tables": shared_tables,
    }
