import logging

from pyramid.request import Request
from pyramid.view import view_config, view_defaults

from zam_repondeur.visam.resources import ConseilResource

logger = logging.getLogger(__name__)


class ConseilResourceBase:
    def __init__(self, context: ConseilResource, request: Request) -> None:
        self.context = context
        self.request = request


@view_defaults(context=ConseilResource)
class ConseilsList(ConseilResourceBase):
    @view_config(request_method="GET", renderer="conseil_item.html")
    def get(self) -> dict:
        return {
            "conseil": self.context.model(),
            "current_tab": "conseils",
        }
