from pyramid.request import Request
from pyramid.view import view_config, view_defaults

from zam_repondeur.visam.resources import ConseilResource


class ConseilViewBase:
    def __init__(self, context: ConseilResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.conseil = self.context.model()


@view_defaults(context=ConseilResource)
class ConseilView(ConseilViewBase):
    @view_config(request_method="GET", renderer="conseil_item.html")
    def get(self) -> dict:
        return {
            "conseil": self.conseil,
            "lectures": self.conseil.lectures,
            "current_tab": "conseils",
            "conseil_resource": self.context,
        }
