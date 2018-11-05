from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import Column, DateTime, Integer, Text, desc
from sqlalchemy.orm import joinedload, relationship

from .amendement import Amendement
from .base import Base, DBSession
from .journal import Journal

CHAMBRES = {"an": "Assemblée nationale", "senat": "Sénat"}

SESSIONS = {
    "an": {"15": "15e législature", "14": "14e législature"},
    "senat": {"2017-2018": "2017-2018"},
}


class Lecture(Base):
    __tablename__ = "lectures"

    pk = Column(Integer, primary_key=True)
    chambre = Column(Text)
    session = Column(Text)
    num_texte = Column(Integer)
    partie = Column(Integer, nullable=True)  # only for PLF
    organe = Column(Text)
    titre = Column(Text)
    dossier_legislatif = Column(Text)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    amendements = relationship(
        Amendement,
        order_by=(Amendement.position, Amendement.num),
        back_populates="lecture",
        cascade="all, delete-orphan",
    )
    articles = relationship(
        "Article", back_populates="lecture", cascade="all, delete-orphan"
    )
    journal = relationship(
        Journal,
        order_by=(Journal.created_at.desc()),
        back_populates="lecture",
        cascade="all, delete-orphan",
    )

    __repr_keys__ = ("pk", "chambre", "session", "organe", "num_texte")

    def __str__(self) -> str:
        return ", ".join(
            [
                self.format_chambre(),
                self.format_session(),
                self.format_organe(),
                self.format_num_lecture(),
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
        from zam_repondeur.data import get_data  # avoid circular imports

        result: str = self.organe
        organes = get_data("organes")
        if self.organe in organes:
            organe_data = organes[self.organe]
            result = organe_data["libelleAbrege"]
        return self.rewrite_organe(result)

    def rewrite_organe(self, label: str) -> str:
        if label in {"Assemblée", "Sénat"}:
            return "Séance publique"
        if label.startswith("Commission"):
            return label
        return f"Commission des {label.lower()}"

    def format_num_lecture(self) -> str:
        num_lecture, title = self.titre.split(" – ", 1)
        return str(num_lecture.strip())

    def format_texte(self) -> str:
        if self.partie == 1:
            partie = " (1re partie)"
        elif self.partie == 2:
            partie = " (2nde partie)"
        else:
            partie = ""
        return f"texte nº\u00a0{self.num_texte}{partie}"

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
    def modified_at_timestamp(self) -> float:
        timestamp: float = (self.modified_at - datetime(1970, 1, 1)).total_seconds()
        return timestamp

    def modified_amendements_numbers_since(self, timestamp: float) -> List[str]:
        if not self.amendements:
            return []
        return [
            str(amendement)
            for amendement in self.amendements
            if amendement.modified_at_timestamp > timestamp
        ]

    @property
    def displayable(self) -> bool:
        return any(amd.is_displayable for amd in self.amendements)

    @classmethod
    def all(cls) -> List["Lecture"]:
        lectures: List["Lecture"] = (
            DBSession.query(cls)
            .options(joinedload("amendements"))
            .order_by(desc(cls.created_at))
            .all()
        )
        return lectures

    @classmethod
    def get(
        cls,
        chambre: str,
        session: str,
        num_texte: int,
        partie: Optional[int],
        organe: str,
        *options: Any,
    ) -> Optional["Lecture"]:
        res: Optional["Lecture"] = (
            DBSession.query(cls)
            .filter(
                cls.chambre == chambre,
                cls.session == session,
                cls.num_texte == num_texte,
                cls.partie == partie,
                cls.organe == organe,
            )
            .options(*options)
            .first()
        )
        return res

    @classmethod
    def exists(
        cls,
        chambre: str,
        session: str,
        num_texte: int,
        partie: Optional[int],
        organe: str,
    ) -> bool:
        res: bool = DBSession.query(
            DBSession.query(cls)
            .filter(
                cls.chambre == chambre,
                cls.session == session,
                cls.num_texte == num_texte,
                cls.partie == partie,
                cls.organe == organe,
            )
            .exists()
        ).scalar()
        return res

    @classmethod
    def create(
        cls,
        chambre: str,
        session: str,
        num_texte: int,
        titre: str,
        organe: str,
        dossier_legislatif: str,
        partie: Optional[int] = None,
    ) -> "Lecture":
        now = datetime.utcnow()
        lecture = cls(
            chambre=chambre,
            session=session,
            num_texte=num_texte,
            partie=partie,
            titre=titre,
            organe=organe,
            dossier_legislatif=dossier_legislatif,
            created_at=now,
            modified_at=now,
        )
        DBSession.add(lecture)
        return lecture

    @property
    def url_key(self) -> str:
        if self.partie is not None:
            partie = f"-{self.partie}"
        else:
            partie = ""
        return f"{self.chambre}.{self.session}.{self.num_texte}{partie}.{self.organe}"
