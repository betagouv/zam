import transaction
from datetime import date
from typing import Dict, List, Optional, Union

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from sqlalchemy.orm import joinedload

from zam_repondeur.data import repository
from zam_repondeur.fetch import get_articles
from zam_repondeur.fetch.an.dossiers.models import Dossier, Lecture
from zam_repondeur.message import Message
from zam_repondeur.models import (
    Batch,
    Chambre,
    DBSession,
    Dossier as DossierModel,
    Lecture as LectureModel,
    Texte as TexteModel,
    User,
    get_one_or_create,
)
from zam_repondeur.models.events.lecture import ArticlesRecuperes, LectureCreee
from zam_repondeur.models.events.amendement import BatchSet, BatchUnset
from zam_repondeur.models.users import Team
from zam_repondeur.resources import (
    AmendementCollection,
    LectureCollection,
    LectureResource,
)
from zam_repondeur.tasks.fetch import fetch_articles, fetch_amendements


@view_config(context=LectureCollection, renderer="lectures_list.html")
def lectures_list(
    context: LectureCollection, request: Request
) -> Union[Response, dict]:

    all_lectures = context.models()

    lectures = [
        lecture
        for lecture in all_lectures
        if lecture.owned_by_team is None or lecture.owned_by_team in request.user.teams
    ]

    if not lectures:
        return HTTPFound(request.resource_url(context, "add"))

    return {"lectures": lectures}


@view_defaults(context=LectureCollection, name="add")
class LecturesAdd:
    def __init__(self, context: LectureCollection, request: Request) -> None:
        self.context = context
        self.request = request
        self.dossiers_by_uid: Dict[str, Dossier] = repository.get_data("dossiers")

    @view_config(request_method="GET", renderer="lectures_add.html")
    def get(self) -> dict:
        lectures = self.context.models()
        return {
            "dossiers": [
                {"uid": uid, "titre": dossier.titre}
                for uid, dossier in self.dossiers_by_uid.items()
            ],
            "lectures": lectures,
            "hide_lectures_link": len(lectures) == 0,
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        dossier_ref = self._get_dossier_ref()
        lecture_ref = self._get_lecture_ref(dossier_ref)

        chambre = lecture_ref.chambre.value
        titre = lecture_ref.titre
        organe = lecture_ref.organe
        partie = lecture_ref.partie
        texte = lecture_ref.texte

        if texte.date_depot is None:
            raise RuntimeError("Cannot create Lecture for Texte with no date_depot")

        texte_model = get_one_or_create(
            TexteModel,
            uid=texte.uid,
            type_=texte.type_,
            chambre=Chambre.AN if lecture_ref.chambre.value == "an" else Chambre.SENAT,
            legislature=texte.legislature,
            session=texte.session,
            numero=texte.numero,
            titre_long=texte.titre_long,
            titre_court=texte.titre_court,
            date_depot=texte.date_depot,
        )[0]

        dossier_model = get_one_or_create(
            DossierModel, uid=dossier_ref.uid, titre=dossier_ref.titre
        )[0]

        if LectureModel.exists(chambre, texte_model, partie, organe):
            self.request.session.flash(
                Message(cls="warning", text="Cette lecture existe déjà…")
            )
            return HTTPFound(location=self.request.resource_url(self.context))

        lecture_model: LectureModel = LectureModel.create(
            owned_by_team=self.request.team,
            texte=texte_model,
            partie=partie,
            titre=titre,
            organe=organe,
            dossier=dossier_model,
        )
        get_articles(lecture_model)
        LectureCreee.create(self.request, lecture=lecture_model)
        ArticlesRecuperes.create(request=None, lecture=lecture_model)
        # Call to fetch_* tasks below being asynchronous, we need to make
        # sure the lecture_model already exists once and for all in the database
        # for future access. Otherwise, it may create many instances and
        # thus many objects within the database.
        transaction.commit()
        fetch_amendements(lecture_model.pk)
        self.request.session.flash(
            Message(
                cls="success",
                text=(
                    "Lecture créée avec succès, amendements en cours de récupération."
                ),
            )
        )
        return HTTPFound(
            location=self.request.resource_url(
                self.context[lecture_model.url_key], "amendements"
            )
        )

    def _get_dossier_ref(self) -> Dossier:
        try:
            dossier_uid = self.request.POST["dossier"]
        except KeyError:
            raise HTTPBadRequest
        try:
            dossier_ref = self.dossiers_by_uid[dossier_uid]
        except KeyError:
            raise HTTPNotFound
        return dossier_ref

    def _get_lecture_ref(self, dossier: Dossier) -> Lecture:
        try:
            texte_uid, organe, partie_str = self.request.POST["lecture"].split("-", 2)
        except (KeyError, ValueError):
            raise HTTPBadRequest
        partie: Optional[int]
        if partie_str == "":
            partie = None
        else:
            partie = int(partie_str)
        matching = [
            lecture
            for lecture in dossier.lectures
            if (
                lecture.texte.uid == texte_uid
                and lecture.organe == organe
                and lecture.partie == partie
            )
        ]
        if len(matching) != 1:
            raise HTTPNotFound
        return matching[0]


@view_defaults(context=LectureResource)
class LectureView:
    def __init__(self, context: LectureResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.lecture = context.model()

    @view_config(request_method="POST")
    def post(self) -> Response:
        if self.request.user.can_delete_lecture:
            DBSession.delete(self.lecture)
            DBSession.flush()
            self.request.session.flash(
                Message(cls="success", text="Lecture supprimée avec succès.")
            )
        else:
            self.request.session.flash(
                Message(
                    cls="warning",
                    text="Vous n’avez pas les droits pour supprimer une lecture.",
                )
            )
        return HTTPFound(location=self.request.resource_url(self.context.parent))


@view_config(context=AmendementCollection, renderer="amendements.html")
def list_amendements(context: AmendementCollection, request: Request) -> dict:
    lecture_resource = context.parent
    lecture = lecture_resource.model(joinedload("articles"), joinedload("user_tables"))
    return {
        "lecture": lecture,
        "lecture_resource": lecture_resource,
        "current_tab": "index",
        "amendements": lecture.amendements,
        "articles": lecture.articles,
    }


@view_defaults(
    context=LectureResource,
    renderer="transfer_amendements.html",
    name="transfer_amendements",
)
class TransferAmendements:
    def __init__(self, context: LectureResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.from_index = bool(request.GET.get("from_index"))
        self.amendements_nums: list = self.request.GET.getall("nums")

    @view_config(request_method="GET")
    def get(self) -> dict:
        from_save = bool(self.request.GET.get("from_save"))
        lecture = self.context.model(joinedload("amendements"))
        my_table = self.request.user.table_for(lecture)
        amendements = [
            amendement
            for amendement in lecture.amendements
            if str(amendement.num) in self.amendements_nums
        ]
        amendements_being_edited = []
        amendements_not_being_edited = []
        amendements_without_table = []
        for amendement in amendements:
            if amendement.user_table:
                if (
                    amendement.is_being_edited
                    and not amendement.user_table.user == self.request.user
                ):
                    amendements_being_edited.append(amendement)
                else:
                    amendements_not_being_edited.append(amendement)
            else:
                amendements_without_table.append(amendement)
        amendements_with_table = amendements_being_edited + amendements_not_being_edited
        show_transfer_to_myself = amendements_without_table or not all(
            amendement.user_table is my_table for amendement in amendements_with_table
        )
        return {
            "lecture": lecture,
            "amendements": amendements,
            "amendements_with_table": amendements_with_table,
            "amendements_being_edited": amendements_being_edited,
            "amendements_not_being_edited": amendements_not_being_edited,
            "amendements_without_table": amendements_without_table,
            "users": self.target_users,
            "from_index": int(self.from_index),
            "from_save": from_save,
            "show_transfer_to_index": bool(amendements_with_table),
            "show_transfer_to_myself": show_transfer_to_myself,
            "back_url": self.back_url,
        }

    @property
    def target_users(self) -> List[User]:
        team: Optional[Team] = self.request.team
        if team is not None:
            return team.everyone_but_me(self.request.user)
        return User.everyone_but_me(self.request.user)

    @property
    def back_url(self) -> str:
        url: str = self.request.GET.get("back")
        if url is None:
            return self.request.resource_url(self.context["amendements"])
        return url


@view_defaults(
    context=LectureResource, renderer="batch_amendements.html", name="batch_amendements"
)
class BatchAmendements:
    def __init__(self, context: LectureResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.lecture = self.context.model(joinedload("amendements"))

    @view_config(request_method="GET")
    def get(self) -> dict:
        amendements_nums: List[int] = self.request.GET.getall("nums")
        amendements = [
            amendement
            for amendement in self.lecture.amendements
            if str(amendement.num) in amendements_nums
        ]
        return {
            "lecture": self.lecture,
            "amendements": amendements,
            "back_url": self.request.resource_url(
                self.context, "tables", self.request.user.email
            ),
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        amendements_nums: List[int] = self.request.POST.getall("nums")
        amendements = [
            amendement
            for amendement in self.lecture.amendements
            if str(amendement.num) in amendements_nums
        ]
        if len(amendements_nums) == 1:
            BatchUnset.create(self.request, amendements[0])
            return HTTPFound(location=self.back_url)

        batch = Batch.create()
        for amendement in amendements:
            if amendement.batch:
                BatchUnset.create(self.request, amendement)
            BatchSet.create(
                self.request, amendement, batch, amendements_nums=amendements_nums
            )
        return HTTPFound(location=self.back_url)

    @property
    def back_url(self) -> str:
        return self.request.resource_url(
            self.context, "tables", self.request.user.email
        )


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
    return HTTPFound(location=request.resource_url(context, "amendements"))


@view_config(route_name="choices_lectures", renderer="json")
def choices_lectures(request: Request) -> dict:
    uid = request.matchdict["uid"]
    dossiers_by_uid = repository.get_data("dossiers")
    dossier = dossiers_by_uid[uid]
    return {
        "lectures": [
            {"key": lecture.key, "label": lecture.label} for lecture in dossier.lectures
        ]
    }


@view_config(context=LectureResource, name="journal", renderer="lecture_journal.html")
def lecture_journal(context: LectureResource, request: Request) -> Response:
    lecture = context.model()
    return {"lecture": lecture, "today": date.today()}


@view_config(context=LectureResource, name="options", renderer="lecture_options.html")
def lecture_options(context: LectureResource, request: Request) -> Response:
    lecture = context.model()
    return {"lecture": lecture, "lecture_resource": context, "current_tab": "options"}
