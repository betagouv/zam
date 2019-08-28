from string import Template
from typing import Any, Optional

from jinja2 import Markup
from pyramid.request import Request

from ..dossier import Dossier
from ..users import User
from .base import Event


class DossierEvent(Event):
    details_template = Template("")

    def __init__(
        self, dossier: Dossier, request: Optional[Request] = None, **kwargs: Any
    ):
        super().__init__(request=request, **kwargs)
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

    def __init__(self, dossier: Dossier, request: Request):
        super().__init__(dossier=dossier, request=request)

    def apply(self) -> None:
        pass


class DossierDesactive(DossierEvent):
    __mapper_args__ = {"polymorphic_identity": "dossier_desactive"}
    icon = "document"

    summary_template = Template(
        "<abbr title='$email'>$user</abbr> a désactivé le dossier."
    )

    def __init__(self, dossier: Dossier, request: Request):
        super().__init__(dossier=dossier, request=request)

    def apply(self) -> None:
        pass


class LecturesRecuperees(DossierEvent):
    __mapper_args__ = {"polymorphic_identity": "lectures_recuperees"}
    icon = "document"

    summary_template = Template("De nouvelles lectures ont été récupérées.")

    def __init__(self, dossier: Dossier, user: User):
        super().__init__(dossier=dossier, user=user)

    def apply(self) -> None:
        pass


class InvitationEnvoyee(DossierEvent):
    __mapper_args__ = {"polymorphic_identity": "invitation_envoyee"}
    icon = "document"

    def __init__(self, dossier: Dossier, email: str, request: Request):
        super().__init__(dossier=dossier, email=email, request=request)

    @property
    def summary_template(self) -> Template:
        email = self.data["email"]
        return Template(f"<abbr title='$email'>$user</abbr> a invité « {email} »")

    def apply(self) -> None:
        pass


class DossierRetrait(DossierEvent):
    __mapper_args__ = {"polymorphic_identity": "dossier_retrait"}
    icon = "document"

    def __init__(self, dossier: Dossier, target: str, request: Request):
        super().__init__(dossier=dossier, target=target, request=request)

    @property
    def summary_template(self) -> Template:
        target = self.data["target"]
        return Template(f"<abbr title='$email'>$user</abbr> a retiré « {target} »")

    def apply(self) -> None:
        pass
