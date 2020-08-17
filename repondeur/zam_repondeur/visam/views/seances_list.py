import logging

from pyramid.request import Request
from pyramid.view import view_config, view_defaults

from zam_repondeur.visam.resources import SeanceCollection

logger = logging.getLogger(__name__)


class SeanceCollectionBase:
    def __init__(self, context: SeanceCollection, request: Request) -> None:
        self.context = context
        self.request = request


@view_defaults(context=SeanceCollection)
class ListSeancesView(SeanceCollectionBase):
    @view_config(request_method="GET", renderer="seances_list.html")
    def get(self) -> dict:
        kwargs = {}
        if not self.request.user.is_admin:
            kwargs["chambres"] = self.request.user.chambres
        seances = self.context.models(**kwargs)

        can_create_seance = self.request.has_permission("create_seance", self.context)

        return {
            "seances": seances,
            "can_create_seance": can_create_seance,
            "current_tab": "seances",
        }
