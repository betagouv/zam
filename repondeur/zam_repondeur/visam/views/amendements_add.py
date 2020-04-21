from typing import Optional

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.message import Message
from zam_repondeur.models import Amendement, Article, DBSession, Lecture
from zam_repondeur.models.division import SubDiv
from zam_repondeur.resources import AmendementCollection
from zam_repondeur.services.clean import clean_html
from zam_repondeur.visam.models import AmendementSaisi, Organisation, UserMembership


@view_defaults(context=AmendementCollection, name="saisie")
class AddAmendementView:
    def __init__(self, context: AmendementCollection, request: Request):
        self.context = context
        self.request = request
        self.lecture: Lecture = self.context.parent.model()
        self.membership: Optional[UserMembership] = self.request.user.membership_of(
            self.lecture.chambre
        )

    @view_config(request_method="GET", renderer="amendements_add.html")
    def get(self) -> dict:
        lecture_resource = self.context.parent
        return {
            "lecture_resource": lecture_resource,
            "dossier_resource": lecture_resource.dossier_resource,
            "current_tab": "saisie-amendement",
            "lecture": self.lecture,
            "can_select_organisation": self.can_select_organisation(),
            "organisations": DBSession.query(Organisation).all(),
            "subdivs": [
                (article.url_key, str(article))
                for article in sorted(self.lecture.articles)
            ],
            "article_collection_url": self.request.resource_path(
                lecture_resource["articles"]
            ),
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        if self.can_select_organisation():
            organisation_name = self.request.POST.get("organisation")
        else:
            if self.membership is None:
                raise HTTPBadRequest
            organisation_name = self.membership.organisation.name

        num = self.next_num_for(organisation_name)
        corps = clean_html(self.request.POST.get("corps", ""))
        expose = clean_html(self.request.POST.get("expose", ""))

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
            groupe=organisation_name,
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

    def can_select_organisation(self) -> bool:
        return self.request.user.is_admin or (
            self.membership is not None and self.membership.organisation.is_gouvernement
        )
