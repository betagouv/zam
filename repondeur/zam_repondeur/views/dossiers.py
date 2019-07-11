import transaction
from operator import attrgetter
from typing import Optional

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.dossiers import get_dossiers_legislatifs_from_cache
from zam_repondeur.fetch.an.dossiers.models import (
    DossierRef,
    DossierRefsByUID,
    LectureRef,
)
from zam_repondeur.message import Message
from zam_repondeur.models import (
    Chambre,
    DBSession,
    Dossier,
    Lecture,
    Texte,
    get_one_or_create,
)
from zam_repondeur.models.events.lecture import LectureCreee
from zam_repondeur.models.organe import ORGANE_SENAT

from zam_repondeur.resources import DossierCollection, DossierResource
from zam_repondeur.tasks.fetch import fetch_amendements, fetch_articles


@view_config(context=DossierCollection, renderer="dossiers_list.html")
def dossiers_list(context: DossierCollection, request: Request) -> dict:
    all_dossiers = context.models()

    dossiers = [
        dossier
        for dossier in all_dossiers
        if dossier.lectures
        and (
            dossier.owned_by_team is None or dossier.owned_by_team in request.user.teams
        )
    ]
    available_dossiers = [dossier for dossier in all_dossiers if not dossier.lectures]

    return {"dossiers": dossiers, "available_dossiers": available_dossiers}


class DossierAddBase:
    def __init__(self, context: DossierCollection, request: Request) -> None:
        self.context = context
        self.request = request
        self.dossiers_by_uid: DossierRefsByUID = get_dossiers_legislatifs_from_cache()


@view_defaults(context=DossierCollection, name="add")
class DossierAddForm(DossierAddBase):
    @view_config(request_method="GET", renderer="dossiers_add.html")
    def get(self) -> dict:
        dossiers = self.context.models()
        dossiers_refs = [
            {"uid": dossier.uid, "titre": dossier.titre}
            for dossier in sorted(
                self.dossiers_by_uid.values(),
                key=attrgetter("most_recent_texte_date"),
                reverse=True,
            )
        ]
        return {
            "dossiers_refs": dossiers_refs,
            "hide_dossiers_link": len(dossiers) == 0,
        }

    @view_config(request_method="POST")
    def post(self) -> Response:

        dossier_ref = self._get_dossier_ref()

        if Dossier.exists(uid=dossier_ref.uid, slug=dossier_ref.slug):
            self.request.session.flash(
                Message(cls="warning", text="Ce dossier existe déjà…")
            )
            return HTTPFound(location=self.request.resource_url(self.context))

        dossier_model, _ = get_one_or_create(
            Dossier,
            uid=dossier_ref.uid,
            titre=dossier_ref.titre,
            slug=dossier_ref.slug,
            owned_by_team=self.request.team,
        )

        for lecture_ref in dossier_ref.lectures:
            self._create_lecture(dossier_model, lecture_ref)

        self.request.session.flash(
            Message(
                cls="success",
                text=("Dossier créé avec succès, lectures en cours de création."),
            )
        )
        return HTTPFound(
            location=self.request.resource_url(self.context[dossier_model.url_key])
        )

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

    def _create_lecture(self, dossier_model: Dossier, lecture_ref: LectureRef) -> None:
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

        if self._lecture_exists(chambre, texte_model, partie, organe):
            return

        lecture_model = Lecture.create(
            texte=texte_model,
            partie=partie,
            titre=titre,
            organe=organe,
            dossier=dossier_model,
        )
        LectureCreee.create(self.request, lecture=lecture_model)
        # Call to fetch_* tasks below being asynchronous, we need to make
        # sure the lecture_model already exists once and for all in the database
        # for future access. Otherwise, it may create many instances and
        # thus many objects within the database.
        transaction.commit()
        fetch_articles(lecture_model.pk)
        fetch_amendements(lecture_model.pk)
        return

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


@view_defaults(context=DossierResource)
class DossierView:
    def __init__(self, context: DossierResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.dossier = context.dossier

    @view_config(request_method="GET", renderer="dossier_item.html")
    def get(self) -> Response:
        return {"dossier": self.dossier, "lectures": self.dossier.lectures}

    @view_config(request_method="POST")
    def post(self) -> Response:
        if self.request.user.can_delete_dossier:
            DBSession.delete(self.dossier)
            DBSession.flush()
            self.request.session.flash(
                Message(cls="success", text="Dossier supprimé avec succès.")
            )
        else:
            self.request.session.flash(
                Message(
                    cls="warning",
                    text="Vous n’avez pas les droits pour supprimer un dossier.",
                )
            )
        return HTTPFound(location=self.request.resource_url(self.context.parent))
