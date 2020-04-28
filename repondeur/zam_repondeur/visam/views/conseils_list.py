import logging

from pyramid.request import Request
from pyramid.view import view_config, view_defaults

from zam_repondeur.visam.resources import ConseilCollection

logger = logging.getLogger(__name__)


class ConseilCollectionBase:
    def __init__(self, context: ConseilCollection, request: Request) -> None:
        self.context = context
        self.request = request


@view_defaults(context=ConseilCollection)
class ListConseilsView(ConseilCollectionBase):
    @view_config(request_method="GET", renderer="conseils_list.html")
    def get(self) -> dict:
        kwargs = {}
        if not self.request.user.is_admin:
            kwargs["chambres"] = self.request.user.chambres
        conseils = self.context.models(**kwargs)

        can_create_seance = self.request.has_permission("create_seance", self.context)

        return {
            "conseils": conseils,
            "can_create_seance": can_create_seance,
            "current_tab": "conseils",
        }
