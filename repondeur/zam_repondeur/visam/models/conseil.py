import datetime
import enum
from typing import Any, Optional

from sqlalchemy import Boolean, CheckConstraint, Column, Date, Enum, Integer

from zam_repondeur.models.base import Base, DBSession
from zam_repondeur.models.chambre import Chambre


class Formation(enum.Enum):
    ASSEMBLEE_PLENIERE = "Assemblée plénière"
    FORMATION_SPECIALISEE = "Formation spécialisée"


class Conseil(Base):
    """
    Une séance d'un conseil
    """

    __tablename__ = "conseils"
    __table_args__ = (CheckConstraint("chambre NOT IN ('AN', 'SENAT')"),)

    id = Column(Integer, primary_key=True)
    chambre = Column(
        Enum(Chambre),
        nullable=False,
        doc="""
        Le conseil concerné (par exemple: CCFP, CSFPE...).
        """,
    )
    date = Column(
        Date,
        nullable=False,
        doc="""
        La date de la séance du conseil.
        """,
    )
    formation = Column(
        Enum(Formation),
        nullable=False,
        doc="""
        Le conseil peut se réunir en assemblée plénière (le cas le plus courant),
        ou en formation spécialisée.
        """,
    )
    urgence_declaree = Column(
        Boolean,
        nullable=False,
        doc="""
        Si le gouvernement déclare l’urgence, alors les délais seront réduits.
        """,
    )

    def __repr__(self) -> str:
        return f"{self.chambre.name} du {self.date.strftime('%x')}"

    @property
    def slug(self) -> str:
        return f"{self.chambre.name.lower()}-{self.date}"

    @classmethod
    def create(
        cls,
        chambre: Chambre,
        formation: Formation,
        date: datetime.date,
        urgence_declaree: bool = False,
    ) -> "Chambre":
        if chambre in {Chambre.AN, Chambre.SENAT}:
            raise ValueError("Chambre invalide")
        conseil = cls(
            chambre=chambre,
            formation=formation,
            date=date,
            urgence_declaree=urgence_declaree,
        )
        DBSession.add(conseil)
        return conseil

    @classmethod
    def get(cls, slug: str, *options: Any) -> Optional["Conseil"]:
        try:
            chambre, date = slug.split("-", 1)
        except ValueError:
            return None
        res: Optional["Conseil"] = DBSession.query(cls).filter(
            cls.chambre == chambre.upper(), cls.date == date,
        ).options(*options).first()
        return res
