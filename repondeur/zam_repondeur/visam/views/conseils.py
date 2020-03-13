import logging

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.message import Message
from zam_repondeur.models import Chambre, Conseil, Formation
from zam_repondeur.services.fetch.dates import parse_date
from zam_repondeur.visam.resources import ConseilCollection

logger = logging.getLogger(__name__)


class ConseilCollectionBase:
    def __init__(self, context: ConseilCollection, request: Request) -> None:
        self.context = context
        self.request = request


@view_defaults(context=ConseilCollection)
class ConseilsList(ConseilCollectionBase):
    @view_config(request_method="GET", renderer="conseils_list.html")
    def get(self) -> dict:
        return {
            "conseils": self.context.models(),
            "can_add_conseil": True,
            "current_tab": "conseils",
        }


@view_defaults(context=ConseilCollection, name="add", permission="add")
class ConseilAddView(ConseilCollectionBase):
    @view_config(request_method="GET", renderer="conseils_add.html")
    def get(self) -> dict:
        return {
            "current_tab": "conseils",
            "chambres": [
                (choice.name, f"{choice.value} ({choice.name})")
                for choice in Chambre.__members__.values()
                if choice.name not in {"AN", "SENAT"}
            ],
            "formations": [
                (choice.name, choice.value) for choice in Formation.__members__.values()
            ],
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        chambre = Chambre.__members__[self.request.POST["chambre"]]
        date = parse_date(self.request.POST["date"])
        formation = Formation.__members__[self.request.POST["formation"]]
        urgence_declaree = bool(int(self.request.POST["urgence_declaree"]))

        if date is None:
            raise HTTPBadRequest("Date invalide")  # TODO: better validation

        Conseil.create(
            chambre=chambre,
            date=date,
            formation=formation,
            urgence_declaree=urgence_declaree,
        )

        self.request.session.flash(
            Message(cls="success", text=("Conseil créé avec succès."),)
        )
        return HTTPFound(location=self.request.resource_url(self.context))
