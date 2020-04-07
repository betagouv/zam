import logging

from pyramid.request import Request
from pyramid.view import view_config, view_defaults

from zam_repondeur.visam.models import Conseil
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
        chambres = self.request.user.chambres
        conseils = self.context.models().filter(Conseil.chambre.in_(chambres))
        return {
            "conseils": conseils,
            "current_tab": "conseils",
        }
