import datetime
import enum
from typing import Any, List, Optional

from sqlalchemy import Boolean, CheckConstraint, Column, Date, Enum, ForeignKey, Integer
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship

from zam_repondeur.models import get_one_or_create
from zam_repondeur.models.base import Base, DBSession
from zam_repondeur.models.chambre import Chambre
from zam_repondeur.models.lecture import Lecture
from zam_repondeur.models.users import Team, User


class SeanceLecture(Base):
    """
    Association object

    https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html#association-object
    """

    __tablename__ = "seances_lectures"

    seance_pk = Column(
        Integer,
        ForeignKey("seances.pk", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    lecture_pk = Column(
        Integer,
        ForeignKey("lectures.pk", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    lecture = relationship("Lecture")

    position = Column(Integer, doc="Ordre des lectures dans un conseil")


class Formation(enum.Enum):
    ASSEMBLEE_PLENIERE = "Assemblée plénière"
    FORMATION_SPECIALISEE = "Formation spécialisée"


class Seance(Base):
    """
    Une séance d'un conseil
    """

    __tablename__ = "seances"
    __table_args__ = (CheckConstraint("chambre NOT IN ('AN', 'SENAT')"),)

    pk = Column(Integer, primary_key=True)
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

    # We use `ordering_list` to automatically map the order of the list
    # to the `position` attribute on the association object.
    # https://docs.sqlalchemy.org/en/13/orm/extensions/orderinglist.html#module-sqlalchemy.ext.orderinglist
    _lectures: List[SeanceLecture] = relationship(
        "SeanceLecture",
        order_by=[SeanceLecture.position],
        collection_class=ordering_list("position"),
        cascade="all, delete-orphan",
    )

    # We use `association_proxy` to hide the intermediate association objects.
    # https://docs.sqlalchemy.org/en/13/orm/extensions/associationproxy.html#module-sqlalchemy.ext.associationproxy
    lectures: List[Lecture] = association_proxy(
        "_lectures", "lecture", creator=lambda lecture: SeanceLecture(lecture=lecture)
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
    ) -> "Seance":
        if chambre in {Chambre.AN, Chambre.SENAT}:
            raise ValueError("Chambre invalide")
        seance = cls(
            chambre=chambre,
            formation=formation,
            date=date,
            urgence_declaree=urgence_declaree,
        )
        team, _ = get_one_or_create(Team, name=seance.slug)
        seance.team = team
        DBSession.add(seance)
        for admin in DBSession.query(User).filter(
            User.admin_at.isnot(None)  # type: ignore
        ):
            admin.teams.append(team)
        return seance

    @classmethod
    def get(cls, slug: str, *options: Any) -> Optional["Seance"]:
        try:
            chambre, date = slug.split("-", 1)
        except ValueError:
            return None
        res: Optional["Seance"] = DBSession.query(cls).filter(
            cls.chambre == chambre.upper(), cls.date == date,
        ).options(*options).first()
        return res
