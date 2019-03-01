import transaction
from datetime import date
from typing import Dict, Optional, Union

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from sqlalchemy.orm import joinedload

from zam_repondeur.data import get_data
from zam_repondeur.fetch import get_articles
from zam_repondeur.fetch.an.dossiers.models import Dossier, Lecture
from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, Amendement, Lecture as LectureModel, User
from zam_repondeur.models.events.lecture import ArticlesRecuperes
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
        self.dossiers_by_uid: Dict[str, Dossier] = get_data("dossiers")

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
        dossier = self._get_dossier()
        lecture = self._get_lecture(dossier)

        chambre = lecture.chambre.value
        num_texte = lecture.texte.numero
        titre = lecture.titre
        organe = lecture.organe
        partie = lecture.partie

        session = lecture.get_session()

        if LectureModel.exists(chambre, session, num_texte, partie, organe):
            self.request.session.flash(
                Message(cls="warning", text="Cette lecture existe déjà…")
            )
            return HTTPFound(location=self.request.resource_url(self.context))

        lecture_model: LectureModel = LectureModel.create(
            owned_by_team=self.request.team,
            chambre=chambre,
            session=session,
            num_texte=num_texte,
            partie=partie,
            titre=titre,
            organe=organe,
            dossier_legislatif=dossier.titre,
        )
        get_articles(lecture_model)
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

    def _get_dossier(self) -> Dossier:
        try:
            dossier_uid = self.request.POST["dossier"]
        except KeyError:
            raise HTTPBadRequest
        try:
            dossier = self.dossiers_by_uid[dossier_uid]
        except KeyError:
            raise HTTPNotFound
        return dossier

    def _get_lecture(self, dossier: Dossier) -> Lecture:
        try:
            texte, organe, partie_str = self.request.POST["lecture"].split("-", 2)
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
                lecture.texte.uid == texte
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
        DBSession.delete(self.lecture)
        DBSession.flush()
        self.request.session.flash(
            Message(cls="success", text="Lecture supprimée avec succès.")
        )
        return HTTPFound(location=self.request.resource_url(self.context.parent))


@view_config(context=AmendementCollection, renderer="amendements.html")
def list_amendements(context: AmendementCollection, request: Request) -> dict:
    lecture = context.parent.model(joinedload("articles"), joinedload("user_tables"))
    return {
        "lecture": lecture,
        "amendements": lecture.amendements,
        "articles": lecture.articles,
        "check_url": request.resource_path(context.parent, "check"),
        "timestamp": lecture.modified_amendements_at_timestamp,
    }


@view_config(
    context=LectureResource,
    renderer="transfer_amendements.html",
    name="transfer_amendements",
)
def transfer_amendements(context: LectureResource, request: Request) -> dict:
    lecture = context.model()
    my_table = request.user.table_for(lecture)
    amendements_nums: list = request.GET.getall("nums")
    from_index = bool(request.GET.get("from_index"))
    amendements = DBSession.query(Amendement).filter(
        Amendement.lecture_pk == lecture.pk,
        Amendement.num.in_(amendements_nums),  # type: ignore
    )
    if request.team:
        users = [user for user in request.team.users if user != request.user]
    else:
        users = DBSession.query(User).filter(User.email != request.user.email)
    amendements = list(amendements)
    return {
        "lecture": lecture,
        "amendements": amendements,
        "users": users,
        "from_index": int(from_index),
        "show_transfer_to_index": any(
            amendement.user_table is not None for amendement in amendements
        ),
        "show_transfer_to_myself": any(
            amendement.user_table is not my_table for amendement in amendements
        ),
    }


@view_config(context=LectureResource, name="manual_refresh")
def manual_refresh(context: LectureResource, request: Request) -> Response:
    lecture = context.model()
    fetch_amendements(lecture.pk)
    fetch_articles(lecture.pk)
    request.session.flash(
        Message(
            cls="success",
            text=(
                "Rafraichissement des amendements et des articles en cours. "
                "Vous serez notifié·e dès que les nouvelles informations "
                "seront disponibles."
            ),
        )
    )
    return HTTPFound(location=request.resource_url(context, "amendements"))


@view_config(context=LectureResource, name="check", renderer="json")
def lecture_check(context: LectureResource, request: Request) -> dict:
    lecture = context.model()
    timestamp = float(request.GET["since"])
    modified_amendements_at_timestamp = lecture.modified_amendements_at_timestamp
    modified_amendements_numbers: list = []
    if timestamp < modified_amendements_at_timestamp:
        modified_amendements_numbers = lecture.modified_amendements_numbers_since(
            timestamp
        )
    return {
        "modified_amendements_numbers": modified_amendements_numbers,
        "modified_at": modified_amendements_at_timestamp,
    }


@view_config(route_name="choices_lectures", renderer="json")
def choices_lectures(request: Request) -> dict:
    uid = request.matchdict["uid"]
    dossiers_by_uid = get_data("dossiers")
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
    return {"lecture": lecture}
