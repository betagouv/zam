from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response

from pyramid.view import view_config, view_defaults

from zam_repondeur.message import Message
from zam_repondeur.models import Amendement, Article, DBSession
from zam_repondeur.models.division import SubDiv
from zam_repondeur.models.events.amendement import AmendementSaisi
from zam_repondeur.resources import AmendementCollection


GROUPES = {
    "LE GOUVERNEMENT": "Gouvernement",
    "employeurs territoriaux": "Employeurs territoriaux",
    "CFE-CGC": "CFE-CGC",
    "CFTC": "CFTC",
    "CGT": "CGT",
    "FA-FP": "FA-FP",
    "FSU": "FSU",
    "UNSA": "UNSA",
}


@view_defaults(context=AmendementCollection, name="saisie")
class SaisieAmendement:
    def __init__(self, context: AmendementCollection, request: Request):
        self.context = context
        self.request = request
        self.lecture = self.context.parent.model()

    @view_config(request_method="GET", renderer="saisie_amendement.html")
    def get(self) -> dict:
        lecture_resource = self.context.parent
        return {
            "lecture_resource": lecture_resource,
            "dossier_resource": lecture_resource.dossier_resource,
            "current_tab": "saisie-amendement",
            "lecture": self.lecture,
            "groupes": GROUPES.items(),
            "subdivs": [
                (article.url_key, str(article))
                for article in sorted(self.lecture.articles)
            ],
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        groupe = self.request.POST.get("groupe")
        num = self.next_num_for(GROUPES[groupe])
        corps = self.request.POST.get("corps")
        expose = self.request.POST.get("expose")

        # Find article
        subdiv = SubDiv(*self.request.POST.get("subdiv").split("."))
        article = (
            DBSession.query(Article)
            .filter_by(
                lecture=self.lecture,
                type=subdiv.type_,
                num=subdiv.num,
                mult=subdiv.mult,
                pos=subdiv.pos,
            )
            .one_or_none()
        )

        max_position = max(
            (
                amdt.position
                for amdt in self.lecture.amendements
                if amdt.position is not None
            ),
            default=0,
        )

        # Create amendement
        amendement = Amendement.create(
            lecture=self.lecture,
            article=article,
            num=num,
            groupe=groupe,
            corps=corps,
            expose=expose,
            position=max_position + 1,
        )

        # Add initial event to journal
        AmendementSaisi.create(amendement=amendement, request=self.request)

        # Show success notification
        self.request.session.flash(
            Message(cls="success", text="Amendement saisi avec succès.")
        )

        # Redirect to index
        index_url = self.request.resource_url(self.context, anchor=amendement.slug)
        return HTTPFound(location=index_url)

    def next_num_for(self, groupe_title: str) -> str:
        nums = (
            DBSession.query(Amendement.num)
            .filter(
                Amendement.lecture == self.lecture,
                Amendement.num.ilike(groupe_title + " %"),  # type: ignore
            )
            .all()
        )
        start = len(groupe_title) + 1
        max_num = max((int(num[start:]) for (num,) in nums), default=0)
        return groupe_title + " " + str(max_num + 1)
