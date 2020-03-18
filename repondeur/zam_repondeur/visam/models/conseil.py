import datetime
import enum
from typing import Any, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    Enum,
    ForeignKey,
    Integer,
    Table,
)
from sqlalchemy.orm import backref, relationship

from zam_repondeur.models import get_one_or_create
from zam_repondeur.models.base import Base, DBSession
from zam_repondeur.models.chambre import Chambre
from zam_repondeur.models.users import Team, User

association_table = Table(
    "conseils_lectures",
    Base.metadata,
    Column("conseil_id", Integer, ForeignKey("conseils.id")),
    Column("lecture_pk", Integer, ForeignKey("lectures.pk")),
)


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

    team_pk = Column(Integer, ForeignKey("teams.pk"), nullable=False)
    team = relationship("Team")

    lectures = relationship(
        "Lecture",
        secondary=association_table,
        backref=backref("_conseil", uselist=False),
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
    ) -> "Conseil":
        if chambre in {Chambre.AN, Chambre.SENAT}:
            raise ValueError("Chambre invalide")
        conseil = cls(
            chambre=chambre,
            formation=formation,
            date=date,
            urgence_declaree=urgence_declaree,
        )
        team, _ = get_one_or_create(Team, name=conseil.slug)
        conseil.team = team
        DBSession.add(conseil)
        for admin in DBSession.query(User).filter(
            User.admin_at.isnot(None)  # type: ignore
        ):
            admin.teams.append(team)
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
