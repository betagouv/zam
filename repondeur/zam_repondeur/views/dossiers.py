from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.dossiers import get_dossiers_legislatifs_from_cache
from zam_repondeur.fetch.an.dossiers.models import DossierRefsByUID
from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, Dossier, Lecture, Team, Texte
from zam_repondeur.models.events.dossier import DossierActive
from zam_repondeur.models.events.lecture import LectureCreee

from zam_repondeur.resources import DossierCollection, DossierResource
from zam_repondeur.tasks.fetch import fetch_amendements, fetch_articles, fetch_lectures


class DossierCollectionBase:
    def __init__(self, context: DossierCollection, request: Request) -> None:
        self.context = context
        self.request = request
        self.dossiers = context.models()


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
        }


@view_defaults(context=DossierCollection, name="add", permission="activate")
class DossierAddForm(DossierCollectionBase):
    @view_config(request_method="GET", renderer="dossiers_add.html")
    def get(self) -> dict:
        available_dossiers = [dossier for dossier in self.dossiers if not dossier.team]
        return {"available_dossiers": available_dossiers}

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
        DossierActive.create(self.request, dossier=dossier)

        dossiers_by_uid: DossierRefsByUID = get_dossiers_legislatifs_from_cache()
        dossier_ref = dossiers_by_uid[dossier.uid]
        for lecture_ref in dossier_ref.lectures:
            texte = Texte.get_or_create_from_ref(lecture_ref.texte, lecture_ref.chambre)
            lecture = Lecture.create_from_ref(lecture_ref, dossier, texte)
            if lecture is not None:
                LectureCreee.create(self.request, lecture=lecture)

                # Schedule task to run in worker
                DBSession.flush()

                fetch_articles(lecture.pk)
                fetch_amendements(lecture.pk)

        self.request.session.flash(
            Message(
                cls="success",
                text=("Dossier créé avec succès, lectures en cours de création."),
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


@view_defaults(context=DossierResource)
class DossierView:
    def __init__(self, context: DossierResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.dossier = context.dossier

    @view_config(request_method="GET", renderer="dossier_item.html")
    def get(self) -> Response:
        return {
            "dossier": self.dossier,
            "lectures": sorted(self.dossier.lectures),
            "allowed_to_delete": self.request.has_permission("delete", self.context),
        }

    @view_config(request_method="POST", permission="delete")
    def post(self) -> Response:
        self.dossier.team = None
        for lecture in self.dossier.lectures:
            DBSession.delete(lecture)
        DBSession.flush()
        self.request.session.flash(
            Message(cls="success", text="Dossier supprimé avec succès.")
        )
        return HTTPFound(location=self.request.resource_url(self.context.parent))


@view_config(context=DossierResource, name="manual_refresh")
def manual_refresh(context: DossierResource, request: Request) -> Response:
    dossier = context.dossier
    fetch_lectures(dossier.pk)
    request.session.flash(
        Message(cls="success", text="Rafraichissement des lectures en cours.")
    )
    return HTTPFound(location=request.resource_url(context))
