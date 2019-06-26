import transaction
from datetime import date
from operator import attrgetter
from typing import Any, List, Optional, Union

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from sqlalchemy.orm import joinedload
from webob.multidict import MultiDict

from zam_repondeur.dossiers import get_dossiers_legislatifs_from_cache
from zam_repondeur.fetch import get_articles
from zam_repondeur.fetch.an.dossiers.models import (
    DossierRef,
    DossierRefsByUID,
    LectureRef,
)
from zam_repondeur.message import Message
from zam_repondeur.models import (
    Amendement,
    Batch,
    Chambre,
    DBSession,
    Dossier,
    Lecture,
    Texte,
    User,
    get_one_or_create,
)
from zam_repondeur.models.amendement import Reponse
from zam_repondeur.models.events.lecture import ArticlesRecuperes, LectureCreee
from zam_repondeur.models.events.amendement import (
    AvisAmendementModifie,
    BatchSet,
    BatchUnset,
    CommentsAmendementModifie,
    ObjetAmendementModifie,
    ReponseAmendementModifiee,
)

from zam_repondeur.models.organe import ORGANE_SENAT
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


class LectureAddBase:
    def __init__(self, context: LectureCollection, request: Request) -> None:
        self.context = context
        self.request = request
        self.dossiers_by_uid: DossierRefsByUID = get_dossiers_legislatifs_from_cache()


@view_defaults(context=LectureCollection, name="add")
class LecturesAddForm(LectureAddBase):
    @view_config(request_method="GET", renderer="lectures_add.html")
    def get(self) -> dict:
        lectures = self.context.models()
        dossiers = [
            {"uid": dossier.uid, "titre": dossier.titre}
            for dossier in sorted(
                self.dossiers_by_uid.values(),
                key=attrgetter("most_recent_texte_date"),
                reverse=True,
            )
        ]
        return {
            "dossiers": dossiers,
            "lectures": lectures,
            "hide_lectures_link": len(lectures) == 0,
        }

    @view_config(request_method="POST")
    def post(self) -> Response:

        dossier_ref = self._get_dossier_ref()
        lecture_ref = self._get_lecture_ref(dossier_ref)

        chambre = lecture_ref.chambre
        titre = lecture_ref.titre
        organe = lecture_ref.organe
        partie = lecture_ref.partie
        texte = lecture_ref.texte

        if texte.date_depot is None:
            raise RuntimeError("Cannot create LectureRef for Texte with no date_depot")

        texte_model, _ = get_one_or_create(
            Texte,
            type_=texte.type_,
            chambre=chambre,
            legislature=texte.legislature,
            session=texte.session,
            numero=texte.numero,
            date_depot=texte.date_depot,
        )

        dossier_model, _ = get_one_or_create(
            Dossier, uid=dossier_ref.uid, titre=dossier_ref.titre
        )

        if self._lecture_exists(chambre, texte_model, partie, organe):
            self.request.session.flash(
                Message(cls="warning", text="Cette lecture existe déjà…")
            )
            return HTTPFound(location=self.request.resource_url(self.context))

        lecture_model: Lecture = Lecture.create(
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

    def _lecture_exists(
        self, chambre: Chambre, texte_model: Texte, partie: Optional[int], organe: str
    ) -> bool:
        if Lecture.exists(chambre, texte_model, partie, organe):
            return True
        # We might already have a Sénat commission lecture created earlier from
        # scraping data, and that would not have the organe.
        if chambre == Chambre.SENAT and organe != ORGANE_SENAT:
            return Lecture.exists(chambre, texte_model, partie, "")
        return False

    def _get_dossier_ref(self) -> DossierRef:
        try:
            dossier_uid = self.request.POST["dossier"]
        except KeyError:
            raise HTTPBadRequest
        try:
            dossier_ref = self.dossiers_by_uid[dossier_uid]
        except KeyError:
            raise HTTPNotFound
        return dossier_ref

    def _get_lecture_ref(self, dossier_ref: DossierRef) -> LectureRef:
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
            lecture_ref
            for lecture_ref in dossier_ref.lectures
            if (
                lecture_ref.texte.uid == texte_uid
                and lecture_ref.organe == organe
                and lecture_ref.partie == partie
            )
        ]
        if len(matching) != 1:
            raise HTTPNotFound
        return matching[0]


class LectureAddChoices(LectureAddBase):
    @view_config(route_name="choices_lectures", request_method="GET", renderer="json")
    def get(self) -> dict:
        uid = self.request.matchdict["uid"]
        dossier = self.dossiers_by_uid[uid]
        return {
            "lectures": [
                {"key": lecture.key, "label": lecture.label}
                for lecture in dossier.lectures
            ]
        }


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
    """
    The index
    """
    lecture_resource = context.parent
    lecture = lecture_resource.model(joinedload("articles"), joinedload("user_tables"))
    return {
        "lecture": lecture,
        "lecture_resource": lecture_resource,
        "current_tab": "index",
        "all_amendements": lecture.amendements,
        "collapsed_amendements": Batch.collapsed_batches(lecture.amendements),
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
        lecture = self.context.model()  # PERFS: do not joinedload("amendements").
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
    def get(self) -> Any:
        amendements = self.get_amendements_from(self.request.GET)

        self.check_amendements_are_all_on_my_table(amendements)
        self.check_amendements_have_all_same_reponse_or_empty(amendements)
        self.check_amendements_are_all_from_same_article(amendements)
        self.check_amendements_are_all_from_same_mission(amendements)

        return {
            "lecture": self.lecture,
            "amendements": amendements,
            "back_url": self.my_table_url,
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        # Special case: unbatch (TODO: move to a separate route)
        if len(self.request.POST.getall("nums")) == 1:
            amendement = self.get_amendements_from(self.request.POST)[0]
            BatchUnset.create(self.request, amendement)
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
                BatchUnset.create(self.request, amendement)
            BatchSet.create(
                self.request,
                amendement,
                batch,
                amendements_nums=[amendement.num for amendement in amendements],
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
                        self.request, amendement, shared_reponse.avis
                    )
                if (amendement.user_content.objet or "") != shared_reponse.objet:
                    ObjetAmendementModifie.create(
                        self.request, amendement, shared_reponse.objet
                    )
                if (amendement.user_content.reponse or "") != shared_reponse.content:
                    ReponseAmendementModifiee.create(
                        self.request, amendement, shared_reponse.content
                    )
                if (amendement.user_content.comments or "") != shared_reponse.comments:
                    CommentsAmendementModifie.create(
                        self.request, amendement, shared_reponse.comments
                    )

        return HTTPFound(location=self.my_table_url)

    @property
    def my_table_url(self) -> str:
        return self.request.resource_url(
            self.context, "tables", self.request.user.email
        )

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
    return HTTPFound(location=request.resource_url(context, "amendements"))


@view_config(context=LectureResource, name="journal", renderer="lecture_journal.html")
def lecture_journal(context: LectureResource, request: Request) -> Response:
    lecture = context.model()
    return {"lecture": lecture, "today": date.today()}


@view_config(context=LectureResource, name="options", renderer="lecture_options.html")
def lecture_options(context: LectureResource, request: Request) -> Response:
    lecture = context.model()
    return {"lecture": lecture, "lecture_resource": context, "current_tab": "options"}
