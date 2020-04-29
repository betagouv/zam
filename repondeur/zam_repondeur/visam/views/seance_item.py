from pyramid.request import Request
from pyramid.view import view_config, view_defaults

from zam_repondeur.visam.resources import SeanceResource


class SeanceViewBase:
    def __init__(self, context: SeanceResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.seance = self.context.model()


@view_defaults(context=SeanceResource)
class SeanceView(SeanceViewBase):
    @view_config(request_method="GET", renderer="seance_item.html")
    def get(self) -> dict:
        has_edit_permission = self.request.has_permission("edit", self.context)
        return {
            "seance": self.seance,
            "lectures": self.seance.lectures,
            "current_tab": "seances",
            "seance_resource": self.context,
            "can_create_texte": has_edit_permission,
            "can_reorder_textes": has_edit_permission and len(self.seance.lectures) > 1,
        }
