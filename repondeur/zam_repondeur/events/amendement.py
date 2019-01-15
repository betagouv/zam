from typing import Any

from sqlalchemy import Column, ForeignKey, Integer

from sqlalchemy.orm import backref, relationship

from .base import Event
from ..models.amendement import Amendement


class AmendementEvent(Event):
    amendement_pk = Column(Integer, ForeignKey("amendements.pk"))
    amendement = relationship(Amendement, backref=backref("events", order_by=Event.created_at.desc()))

    def __init__(self, amendement: Amendement, **kwargs: Any):
        super().__init__(**kwargs)
        self.amendement = amendement


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

    action = "${USER} a donné l’avis ${NEW_VALUE}"

    def __init__(self, amendement: Amendement, avis: str) -> None:
        super().__init__(
            amendement, old_value=amendement.user_content.avis, new_value=avis
        )

    def apply(self) -> None:
        self.amendement.user_content.avis = self.data["new_value"]


class UpdateAmendementAffectation(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "update_amendement_affectation"}

    action = "${USER} a affecté l’amendement à ${NEW_VALUE}"

    def __init__(self, amendement: Amendement, avis: str) -> None:
        super().__init__(
            amendement, old_value=amendement.user_content.avis, new_value=avis
        )

    def apply(self) -> None:
        self.amendement.user_content.avis = self.data["new_value"]
