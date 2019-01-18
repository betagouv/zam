from string import Template
from typing import Any

from jinja2 import Markup
from jinja2.filters import do_striptags
from sqlalchemy import Column, ForeignKey, Integer

from sqlalchemy.orm import backref, relationship

from .base import Event
from ..models.amendement import Amendement


class AmendementEvent(Event):
    amendement_pk = Column(Integer, ForeignKey("amendements.pk"))
    amendement = relationship(
        Amendement, backref=backref("events", order_by=Event.created_at.desc())
    )

    summary_template = Template("<abbr title='$email'>$user</abbr>")
    details_template = Template(
        "De <del>« $old_value »</del> à <ins>« $new_value »</ins>"
    )

    def __init__(self, amendement: Amendement, **kwargs: Any):
        super().__init__(**kwargs)
        self.amendement = amendement
        self.template_vars = {
            "user": self.user.display_name,
            "email": self.user.email,
            "new_value": do_striptags(self.data["new_value"]),
            "old_value": do_striptags(self.data["old_value"]),
        }

    def render_summary(self) -> str:
        return Markup(self.summary_template.safe_substitute(**self.template_vars))

    def render_details(self) -> str:
        return Markup(self.details_template.safe_substitute(**self.template_vars))


class AmendementIrrecevable(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "amendement_irrecevable"}

    @property
    def action(self):
        if self.amendement.lecture.chambre == "an":
            de_qui = "de l’Asssemblée nationale"
        else:
            de_qui = "du Sénat"
        return f"L’amendement a été déclaré irrecevable par les services {de_qui}"


class UpdateAmendementAvis(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "update_amendement_avis"}

    summary_template = Template(
        "<abbr title='$email'>$user</abbr> a changé l’avis de $old_value à $new_value"
    )
    details_template = Template("")

    def __init__(self, amendement: Amendement, avis: str) -> None:
        super().__init__(
            amendement, old_value=amendement.user_content.avis, new_value=avis
        )

    def apply(self) -> None:
        self.amendement.user_content.avis = self.data["new_value"]


class UpdateAmendementObjet(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "update_amendement_objet"}

    summary_template = Template("<abbr title='$email'>$user</abbr> a changé l’objet")

    def __init__(self, amendement: Amendement, objet: str) -> None:
        super().__init__(
            amendement, old_value=amendement.user_content.objet, new_value=objet
        )

    def apply(self) -> None:
        self.amendement.user_content.objet = self.data["new_value"]


class UpdateAmendementReponse(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "update_amendement_reponse"}

    summary_template = Template("<abbr title='$email'>$user</abbr> a changé la réponse")

    def __init__(self, amendement: Amendement, reponse: str) -> None:
        super().__init__(
            amendement, old_value=amendement.user_content.reponse, new_value=reponse
        )

    def apply(self) -> None:
        self.amendement.user_content.reponse = self.data["new_value"]


class UpdateAmendementAffectation(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "update_amendement_affectation"}

    summary_template = Template(
        "<abbr title='$email'>$user</abbr> a affecté l’amendement "
        "de $old_value à $new_value"
    )
    details_template = Template("")

    def __init__(self, amendement: Amendement, avis: str) -> None:
        super().__init__(
            amendement, old_value=amendement.user_content.avis, new_value=avis
        )

    def apply(self) -> None:
        self.amendement.user_content.avis = self.data["new_value"]
