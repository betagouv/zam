import logging

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.message import Message
from zam_repondeur.models import Chambre, get_one_or_create
from zam_repondeur.services.fetch.dates import parse_date
from zam_repondeur.visam.models import Formation, Seance
from zam_repondeur.visam.resources import SeanceCollection
from zam_repondeur.visam.views.seances_list import SeanceCollectionBase

logger = logging.getLogger(__name__)


@view_defaults(context=SeanceCollection, name="add", permission="create_seance")
class AddSeanceView(SeanceCollectionBase):
    @view_config(request_method="GET", renderer="seances_add.html")
    def get(self) -> dict:
        return {
            "current_tab": "seances",
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

        seance, created = get_one_or_create(
            Seance,
            chambre=chambre,
            date=date,
            formation=formation,
            urgence_declaree=urgence_declaree,
        )

        if created:
            self.request.session.flash(
                Message(cls="success", text="Séance créée avec succès.")
            )
        else:
            self.request.session.flash(
                Message(cls="warning", text="Cette séance existe déjà…")
            )
        return HTTPFound(location=self.request.resource_url(self.context, seance.slug))
