from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import relationship

from .base import Base, DBSession

# Make these types available to mypy, but avoid circular imports
if TYPE_CHECKING:
    from .amendement import Amendement  # noqa


class Mission(Base):
    __tablename__ = "missions"

    pk: int = Column(Integer, primary_key=True)
    titre: Optional[str] = Column(Text, nullable=True)
    titre_court: Optional[str] = Column(Text, nullable=True)

    amendements: List["Amendement"] = relationship(
        "Amendement", back_populates="mission", cascade="all, delete-orphan"
    )

    __repr_keys__ = ("pk", "titre", "titre_court")

    @classmethod
    def create(
        cls, titre: Optional[str] = None, titre_court: Optional[str] = None
    ) -> "Mission":
        mission = cls(titre=titre, titre_court=titre_court)
        DBSession.add(mission)
        return mission
