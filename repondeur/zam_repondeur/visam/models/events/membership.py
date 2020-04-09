from string import Template
from typing import Any, Optional

from jinja2 import Markup
from pyramid.request import Request

from zam_repondeur.models.base import DBSession
from zam_repondeur.models.chambre import Chambre
from zam_repondeur.models.events.base import Event
from zam_repondeur.models.users import User

from ..membership import UserChambreMembership


class MembershipEvent(Event):
    details_template = Template("")

    @property
    def template_vars(self) -> dict:
        template_vars = {
            "target_user": self.data["target_user"],
            "target_chambre": self.data["target_chambre"],
        }
        if self.user:
            template_vars.update({"user": self.user.name, "email": self.user.email})
        return template_vars

    def render_summary(self) -> str:
        return Markup(self.summary_template.safe_substitute(**self.template_vars))

    def render_details(self) -> str:
        return Markup(self.details_template.safe_substitute(**self.template_vars))


class MembershipAdded(MembershipEvent):
    __mapper_args__ = {"polymorphic_identity": "membership_added"}
    icon = "edit"

    def __init__(
        self,
        target_user: User,
        target_chambre: Chambre,
        comment: Optional[str],
        request: Optional[Request] = None,
        **kwargs: Any,
    ):
        kwargs["target_user"] = str(target_user)
        kwargs["target_chambre"] = target_chambre.value
        super().__init__(request=request, **kwargs)
        self.target_user = target_user
        self.target_chambre = target_chambre

    @property
    def summary_template(self) -> Template:
        if self.user:
            who = "<abbr title='$email'>$user</abbr>"
        else:
            who = "L’équipe technique"
        return Template(f"{who} a ajouté $target_user au $target_chambre.")

    def apply(self) -> None:
        UserChambreMembership.create(user=self.target_user, chambre=self.target_chambre)


class MembershipRemoved(MembershipEvent):
    __mapper_args__ = {"polymorphic_identity": "membership_removed"}
    icon = "edit"

    def __init__(
        self,
        membership: UserChambreMembership,
        request: Optional[Request] = None,
        **kwargs: Any,
    ):
        kwargs["target_user"] = str(membership.user)
        kwargs["target_chambre"] = membership.chambre.value
        super().__init__(request=request, **kwargs)
        self.membership = membership

    @property
    def summary_template(self) -> Template:
        if self.user:
            who = "<abbr title='$email'>$user</abbr>"
        else:
            who = "L’équipe technique"
        return Template(f"{who} a retiré $target_user du $target_chambre.")

    def apply(self) -> None:
        DBSession.delete(self.membership)
