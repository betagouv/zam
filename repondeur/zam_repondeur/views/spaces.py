from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.models import DBSession, Amendement, User
from zam_repondeur.models.events.amendement import AmendementTransfere
from zam_repondeur.resources import SpaceResource


@view_defaults(context=SpaceResource)
class SpaceView:
    def __init__(self, context: SpaceResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.lecture = context.lecture_resource.model()
        self.owner = (
            DBSession.query(User).filter(User.email == self.context.email).first()
        )

    @view_config(request_method="GET", renderer="space_detail.html")
    def get(self) -> dict:
        return {
            "lecture": self.lecture,
            "amendements": self.context.amendements(),
            "is_owner": self.owner.email == self.request.user.email,
            "owner": self.owner,
            "users": DBSession.query(User).filter(
                User.email != self.request.user.email, User.email != self.owner.email
            ),
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        num = self.request.POST.get("num")
        target = self.request.POST.get("target")
        old = ""
        new = ""
        if target is None or target == self.owner.email:
            target = self.owner
        else:
            target = DBSession.query(User).filter(User.email == target).first()
        amendement = (
            DBSession.query(Amendement)
            .filter(Amendement.lecture == self.lecture, Amendement.num == num)
            .first()
        )
        if amendement in target.space.amendements:
            amendement.user_space = None
            old = str(target)
        else:
            if amendement.user_space:
                old = str(amendement.user_space.user)
            new = str(target)
            target.space.amendements.append(amendement)
        AmendementTransfere.create(self.request, amendement, old, new)
        return HTTPFound(
            location=self.request.resource_url(self.context.parent, self.owner.email)
        )
