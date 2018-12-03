import transaction
from typing import Dict, Optional, Union

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from sqlalchemy.orm import joinedload

from zam_repondeur.data import get_data
from zam_repondeur.fetch.an.dossiers.models import Dossier, Lecture
from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, Lecture as LectureModel
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
    lectures = context.models()
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
                Message(cls="warning", text="Cette lecture existe déjà...")
            )
            return HTTPFound(location=self.request.resource_url(self.context))

        lecture_model: LectureModel = LectureModel.create(
            chambre=chambre,
            session=session,
            num_texte=num_texte,
            partie=partie,
            titre=titre,
            organe=organe,
            dossier_legislatif=dossier.titre,
        )
        # Call to fetch_* tasks below being asynchronous, we need to make
        # sure the lecture_model already exists once and for all in the database
        # for future access. Otherwise, it may create many instances and
        # thus many objects within the database.
        transaction.commit()
        fetch_amendements(lecture_model.pk)
        fetch_articles(lecture_model.pk)
        self.request.session.flash(
            Message(
                cls="success",
                text=(
                    "Lecture créée avec succès, amendements et articles "
                    "en cours de récupération."
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


@view_defaults(context=AmendementCollection)
class ListAmendements:
    def __init__(self, context: AmendementCollection, request: Request) -> None:
        self.context = context
        self.request = request
        self.lecture = context.parent.model(joinedload("articles"))
        self.amendements = self.lecture.amendements
        self.articles = self.lecture.articles

    @view_config(request_method="GET", renderer="amendements.html")
    def get(self) -> dict:
        check_url = self.request.resource_path(self.context.parent, "check")
        return {
            "lecture": self.lecture,
            "amendements": self.amendements,
            "articles": self.articles,
            "check_url": check_url,
            "timestamp": self.lecture.modified_at_timestamp,
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
    modified_at = lecture.modified_at_timestamp
    modified_amendements_numbers: list = []
    if timestamp < modified_at:
        modified_amendements_numbers = lecture.modified_amendements_numbers_since(
            timestamp
        )
    return {
        "modified_amendements_numbers": modified_amendements_numbers,
        "modified_at": modified_at,
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
