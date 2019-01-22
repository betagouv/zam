from string import Template
from typing import Any

from jinja2 import Markup
from jinja2.filters import do_striptags
from pyramid.request import Request
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import backref, relationship

from .base import Event
from ..amendement import Amendement


class AmendementEvent(Event):
    amendement_pk = Column(Integer, ForeignKey("amendements.pk"))
    amendement = relationship(
        Amendement, backref=backref("events", order_by=Event.created_at.desc())
    )

    summary_template = Template("<abbr title='$email'>$user</abbr>")
    details_template = Template(
        "De <del>« $old_value »</del> à <ins>« $new_value »</ins>"
    )
    icon = ""

    def __init__(self, request: Request, amendement: Amendement, **kwargs: Any):
        super().__init__(request, **kwargs)
        self.amendement = amendement

    @property
    def template_vars(self) -> dict:
        template_vars = {
            "new_value": do_striptags(self.data["new_value"]),  # type: ignore
            "old_value": do_striptags(self.data["old_value"]),  # type: ignore
        }
        if self.user:
            template_vars.update(
                {"user": self.user.display_name, "email": self.user.email}
            )
        return template_vars

    def render_summary(self) -> str:
        return Markup(self.summary_template.safe_substitute(**self.template_vars))

    def render_details(self) -> str:
        return Markup(self.details_template.safe_substitute(**self.template_vars))


class AmendementRectifie(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "amendement_rectifie"}
    icon = "edit"

    @property
    def summary_template(self) -> Template:  # type: ignore
        if self.amendement.lecture.chambre == "an":
            de_qui = "de l’Asssemblée nationale"
        else:
            de_qui = "du Sénat"
        return Template(f"L’amendement a été rectifié par les services {de_qui}")

    details_template = Template("")

    def __init__(
        self, request: Request, amendement: Amendement, rectif: str, **kwargs: Any
    ) -> None:
        super().__init__(
            request, amendement, old_value=amendement.rectif, new_value=rectif, **kwargs
        )

    def apply(self) -> None:
        self.amendement.rectif = self.data["new_value"]


class AmendementIrrecevable(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "amendement_irrecevable"}
    icon = "times"

    @property
    def summary_template(self) -> Template:  # type: ignore
        if self.amendement.lecture.chambre == "an":
            de_qui = "de l’Asssemblée nationale"
        else:
            de_qui = "du Sénat"
        return Template(
            f"L’amendement a été déclaré irrecevable par les services {de_qui}"
        )

    details_template = Template("")

    def __init__(
        self, request: Request, amendement: Amendement, sort: str, **kwargs: Any
    ) -> None:
        super().__init__(
            request, amendement, old_value=amendement.sort, new_value=sort, **kwargs
        )

    def apply(self) -> None:
        self.amendement.sort = self.data["new_value"]


class AmendementTransfere(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "amendement_transfere"}

    details_template = Template("")
    icon = "arrow-right"

    @property
    def summary_template(self) -> Template:  # type: ignore
        if self.template_vars["old_value"]:
            template = (
                "<abbr title='$email'>$user</abbr> a transféré l’amendement "
                "de « $old_value » à « $new_value »"
            )
        else:
            template = (
                "<abbr title='$email'>$user</abbr> a transféré l’amendement "
                "à « $new_value »"
            )
        return Template(template)

    def __init__(
        self, request: Request, amendement: Amendement, affectation: str, **kwargs: Any
    ) -> None:
        super().__init__(
            request,
            amendement,
            old_value=amendement.user_content.affectation or "",
            new_value=affectation,
            **kwargs,
        )

    def apply(self) -> None:
        self.amendement.user_content.affectation = self.data["new_value"]


class CorpsAmendementModifie(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "corps_amendement_modifie"}
    icon = "pencil-alt"

    @property
    def summary_template(self) -> Template:  # type: ignore
        if self.amendement.lecture.chambre == "an":
            de_qui = "de l’Asssemblée nationale"
        else:
            de_qui = "du Sénat"
        return Template(
            f"Le corps de l’amendement a été modifié par les services {de_qui}"
        )

    def __init__(
        self, request: Request, amendement: Amendement, corps: str, **kwargs: Any
    ) -> None:
        super().__init__(
            request,
            amendement,
            old_value=amendement.corps or "",
            new_value=corps,
            **kwargs,
        )

    def apply(self) -> None:
        self.amendement.corps = self.data["new_value"]


class ExposeAmendementModifie(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "expose_amendement_modifie"}
    icon = "pencil-alt"

    @property
    def summary_template(self) -> Template:  # type: ignore
        if self.amendement.lecture.chambre == "an":
            de_qui = "de l’Asssemblée nationale"
        else:
            de_qui = "du Sénat"
        return Template(
            f"L’exposé de l’amendement a été modifié par les services {de_qui}"
        )

    def __init__(
        self, request: Request, amendement: Amendement, expose: str, **kwargs: Any
    ) -> None:
        super().__init__(
            request,
            amendement,
            old_value=amendement.expose or "",
            new_value=expose,
            **kwargs,
        )

    def apply(self) -> None:
        self.amendement.expose = self.data["new_value"]


class AvisAmendementModifie(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "avis_amendement_modifie"}

    details_template = Template("")
    icon = "certificate"

    def __init__(
        self, request: Request, amendement: Amendement, avis: str, **kwargs: Any
    ) -> None:
        super().__init__(
            request,
            amendement,
            old_value=amendement.user_content.avis or "",
            new_value=avis,
            **kwargs,
        )

    def apply(self) -> None:
        self.amendement.user_content.avis = self.data["new_value"]

    @property
    def summary_template(self) -> Template:  # type: ignore
        if self.template_vars["old_value"]:
            template = (
                "<abbr title='$email'>$user</abbr> a modifié l’avis "
                "de « $old_value » à « $new_value »"
            )
        else:
            template = "<abbr title='$email'>$user</abbr> a mis l’avis à « $new_value »"
        return Template(template)


class ObjetAmendementModifie(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "objet_modifie"}

    summary_template = Template("<abbr title='$email'>$user</abbr> a modifié l’objet")
    icon = "user-edit"

    def __init__(
        self, request: Request, amendement: Amendement, objet: str, **kwargs: Any
    ) -> None:
        super().__init__(
            request,
            amendement,
            old_value=amendement.user_content.objet or "",
            new_value=objet,
            **kwargs,
        )

    def apply(self) -> None:
        self.amendement.user_content.objet = self.data["new_value"]


class ReponseAmendementModifiee(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "reponse_amendement_modifiee"}

    summary_template = Template(
        "<abbr title='$email'>$user</abbr> a modifié la réponse"
    )
    icon = "user-edit"

    def __init__(
        self, request: Request, amendement: Amendement, reponse: str, **kwargs: Any
    ) -> None:
        super().__init__(
            request,
            amendement,
            old_value=amendement.user_content.reponse or "",
            new_value=reponse,
            **kwargs,
        )

    def apply(self) -> None:
        self.amendement.user_content.reponse = self.data["new_value"]
