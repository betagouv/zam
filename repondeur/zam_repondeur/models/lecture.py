from datetime import datetime
from typing import Any, List

from sqlalchemy import Column, DateTime, Integer, Text, desc

from zam_repondeur.data import get_data

from .amendement import Amendement
from .base import Base, DBSession


CHAMBRES = {"an": "Assemblée nationale", "senat": "Sénat"}

SESSIONS = {
    "an": {"15": "15e législature", "14": "14e législature"},
    "senat": {"2017-2018": "2017-2018"},
}


class Lecture(Base):  # type: ignore
    __tablename__ = "lectures"

    chambre = Column(Text, primary_key=True)
    session = Column(Text, primary_key=True)
    num_texte = Column(Integer, primary_key=True)
    organe = Column(Text, primary_key=True)
    titre = Column(Text)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)

    def __str__(self) -> str:
        return ", ".join(
            [
                self.format_chambre(),
                self.format_session(),
                self.format_organe(),
                self.format_texte(),
            ]
        )

    def format_chambre(self) -> str:
        return CHAMBRES[self.chambre]

    def format_session(self) -> str:
        if self.chambre == "an":
            return f"{self.session}e législature"
        else:
            return f"session {self.session}"

    def format_organe(self) -> str:
        result: str = self.organe
        organes = get_data("organes")
        if self.organe in organes:
            organe_data = organes[self.organe]
            result = organe_data["libelleAbrege"]
        return self.rewrite_organe(result)

    def rewrite_organe(self, label: str) -> str:
        if label in {"Assemblée", "Sénat"}:
            return "Séance publique"
        return f"Commission des {label.lower()}"

    def format_texte(self) -> str:
        return f"texte nº {self.num_texte}"

    def __lt__(self, other: Any) -> bool:
        if type(self) != type(other):
            return NotImplemented
        return (self.chambre, self.session, self.num_texte, self.organe) < (
            other.chambre,
            other.session,
            other.num_texte,
            other.organe,
        )

    @property
    def displayable(self) -> bool:
        query = DBSession.query(Amendement).filter(
            Amendement.chambre == self.chambre,
            Amendement.session == self.session,
            Amendement.num_texte == self.num_texte,
            Amendement.organe == self.organe,
        )
        return any(amd.is_displayable for amd in query)

    @classmethod
    def all(cls) -> List["Lecture"]:
        lectures: List["Lecture"] = DBSession.query(cls).order_by(
            desc(cls.created_at)
        ).all()
        return lectures

    @classmethod
    def get(cls, chambre: str, session: str, num_texte: int, organe: str) -> "Lecture":
        res: "Lecture" = (
            DBSession.query(cls)
            .filter(
                cls.chambre == chambre,
                cls.session == session,
                cls.num_texte == num_texte,
                cls.organe == organe,
            )
            .first()
        )
        return res

    @classmethod
    def exists(cls, chambre: str, session: str, num_texte: int, organe: str) -> bool:
        res: bool = DBSession.query(
            DBSession.query(cls)
            .filter(
                cls.chambre == chambre,
                cls.session == session,
                cls.num_texte == num_texte,
                cls.organe == organe,
            )
            .exists()
        ).scalar()
        return res

    @classmethod
    def create(
        cls, chambre: str, session: str, num_texte: int, titre: str, organe: str
    ) -> "Lecture":
        now = datetime.utcnow()
        lecture = cls(
            chambre=chambre,
            session=session,
            num_texte=num_texte,
            titre=titre,
            organe=organe,
            created_at=now,
            modified_at=now,
        )
        DBSession.add(lecture)
        return lecture
