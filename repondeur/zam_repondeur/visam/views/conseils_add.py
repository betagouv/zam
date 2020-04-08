import logging

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.message import Message
from zam_repondeur.models import Chambre, get_one_or_create
from zam_repondeur.services.fetch.dates import parse_date
from zam_repondeur.visam.models import Conseil, Formation
from zam_repondeur.visam.resources import ConseilCollection
from zam_repondeur.visam.views.conseils_list import ConseilCollectionBase

logger = logging.getLogger(__name__)


@view_defaults(context=ConseilCollection, name="add")
class AddConseilView(ConseilCollectionBase):
    @view_config(request_method="GET", renderer="conseils_add.html")
    def get(self) -> dict:
        return {
            "current_tab": "conseils",
            "chambres": [
                (choice.name, f"{choice.value} ({choice.name})")
                for choice in Chambre.__members__.values()
                if choice.name not in {"AN", "SENAT"}
                and (self.request.user.is_admin or choice in self.request.user.chambres)
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

        if chambre not in self.request.user.chambres:
            # TODO: better validation
            raise HTTPBadRequest("Chambre invalide pour cet·te utilisateur·ice")

        conseil, created = get_one_or_create(
            Conseil,
            chambre=chambre,
            date=date,
            formation=formation,
            urgence_declaree=urgence_declaree,
        )

        if created:
            self.request.session.flash(
                Message(cls="success", text="Conseil créé avec succès.")
            )
        else:
            self.request.session.flash(
                Message(cls="warning", text="Ce conseil existe déjà…")
            )
        return HTTPFound(location=self.request.resource_url(self.context, conseil.slug))
