from string import Template
from typing import Any, Optional

from jinja2 import Markup
from pyramid.request import Request

from ..base import DBSession
from ..users import AllowedEmailPattern
from .base import Event


class WhitelistEvent(Event):
    details_template = Template("")

    @property
    def template_vars(self) -> dict:
        template_vars = {"pattern": self.data["pattern"]}
        if self.user:
            template_vars.update({"user": self.user.name, "email": self.user.email})
        return template_vars

    def render_summary(self) -> str:
        return Markup(self.summary_template.safe_substitute(**self.template_vars))

    def render_details(self) -> str:
        return Markup(self.details_template.safe_substitute(**self.template_vars))


class WhitelistAdd(WhitelistEvent):
    __mapper_args__ = {"polymorphic_identity": "whitelist_add"}
    icon = "edit"

    def __init__(
        self,
        email_pattern: str,
        comment: Optional[str],
        request: Optional[Request] = None,
        **kwargs: Any,
    ):
        kwargs["pattern"] = email_pattern
        super().__init__(request=request, **kwargs)
        self.email_pattern = email_pattern
        self.comment = comment

    @property
    def summary_template(self) -> Template:
        if self.user:
            who = "<abbr title='$email'>$user</abbr>"
        else:
            who = "L’équipe technique"
        return Template(f"{who} a ajouté $pattern à la liste blanche.")

    def apply(self) -> None:
        AllowedEmailPattern.create(pattern=self.email_pattern, comment=self.comment)


class WhitelistRemove(WhitelistEvent):
    __mapper_args__ = {"polymorphic_identity": "whitelist_remove"}
    icon = "edit"

    def __init__(
        self,
        allowed_email_pattern: AllowedEmailPattern,
        request: Optional[Request] = None,
        **kwargs: Any,
    ):
        kwargs["pattern"] = allowed_email_pattern.pattern
        super().__init__(request=request, **kwargs)
        self.allowed_email_pattern = allowed_email_pattern

    @property
    def summary_template(self) -> Template:
        if self.user:
            who = "<abbr title='$email'>$user</abbr>"
        else:
            who = "L’équipe technique"
        return Template(f"{who} a retiré $pattern de la liste blanche.")

    def apply(self) -> None:
        DBSession.delete(self.allowed_email_pattern)
