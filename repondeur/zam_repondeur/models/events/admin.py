from string import Template
from typing import Any, Optional

from jinja2 import Markup
from pyramid.request import Request

from ..users import User
from .base import Event


class AdminEvent(Event):
    details_template = Template("")

    def __init__(self, target: User, request: Optional[Request] = None, **kwargs: Any):
        kwargs["target_user"] = str(target)
        kwargs["target_email"] = target.email
        super().__init__(request=request, **kwargs)

    @property
    def template_vars(self) -> dict:
        return {
            "user": self.user.name,
            "email": self.user.email,
            "target_user": self.data["target_user"],
            "target_email": self.data["target_email"],
        }

    def render_summary(self) -> str:
        return Markup(self.summary_template.safe_substitute(**self.template_vars))

    def render_details(self) -> str:
        return Markup(self.details_template.safe_substitute(**self.template_vars))

    def apply(self) -> None:
        pass


class AdminGrant(AdminEvent):
    __mapper_args__ = {"polymorphic_identity": "admin_grant"}
    icon = "edit"

    summary_template = Template(
        "<abbr title='$email'>$user</abbr> a ajouté "
        "<abbr title='$target_email'>$target_user</abbr> "
        "à la liste des administrateur·ice·s."
    )


class AdminRevoke(AdminEvent):
    __mapper_args__ = {"polymorphic_identity": "admin_revoke"}
    icon = "edit"

    summary_template = Template(
        "<abbr title='$email'>$user</abbr> a retiré "
        "<abbr title='$target_email'>$target_user</abbr> "
        "de la liste des administrateur·ice·s."
    )
