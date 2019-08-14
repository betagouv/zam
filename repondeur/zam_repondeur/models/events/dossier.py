from typing import Any
from string import Template

from jinja2 import Markup
from pyramid.request import Request

from .base import Event
from ..dossier import Dossier


class DossierEvent(Event):
    details_template = Template("")

    def __init__(self, request: Request, dossier: Dossier, **kwargs: Any):
        super().__init__(request, **kwargs)
        self.dossier = dossier

    @property
    def template_vars(self) -> dict:
        if self.user:
            return {"user": self.user.name, "email": self.user.email}
        return {}

    def render_summary(self) -> str:
        return Markup(self.summary_template.safe_substitute(**self.template_vars))

    def render_details(self) -> str:
        return Markup(self.details_template.safe_substitute(**self.template_vars))


class DossierActive(DossierEvent):
    __mapper_args__ = {"polymorphic_identity": "dossier_active"}
    icon = "document"

    summary_template = Template(
        "<abbr title='$email'>$user</abbr> a activé le dossier."
    )

    def apply(self) -> None:
        pass


class LecturesRecuperees(DossierEvent):
    __mapper_args__ = {"polymorphic_identity": "lectures_recuperees"}
    icon = "document"

    summary_template = Template("Les lectures ont été récupérées.")

    def apply(self) -> None:
        pass


class InvitationEnvoyee(DossierEvent):
    __mapper_args__ = {"polymorphic_identity": "invitation_envoyee"}
    icon = "document"

    @property
    def summary_template(self) -> Template:
        email = self.data["email"]
        return Template(f"<abbr title='$email'>$user</abbr> a invité « {email} »")

    def apply(self) -> None:
        pass
