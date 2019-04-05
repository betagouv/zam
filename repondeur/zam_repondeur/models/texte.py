from datetime import datetime
from typing import Optional
import enum

from sqlalchemy import Column, Date, DateTime, Enum, Index, Integer, Text
from sqlalchemy.orm import relationship

from .base import Base, DBSession


class TypeTexte(enum.Enum):
    PROJET = "Projet de loi"
    PROPOSITION = "Proposition de loi"

    @staticmethod
    def from_dict(texte: dict) -> "TypeTexte":
        code = texte["classification"]["type"]["code"]
        if code == "PRJL":
            return TypeTexte.PROJET
        if code == "PION":
            return TypeTexte.PROPOSITION
        raise ValueError(f"Unknown texte type {code}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"


class Chambre(enum.Enum):
    AN = "Assemblée nationale"
    SENAT = "Sénat"

    @staticmethod
    def from_string(chambre: str) -> "Chambre":
        if chambre == "an":
            return Chambre.AN
        if chambre == "senat":
            return Chambre.SENAT
        raise ValueError(f"Invalid string value {chambre!r} for Chambre")


class Texte(Base):
    __tablename__ = "textes"
    __table_args__ = (
        Index(
            "uq_textes_chambre_session_legislature_numero_key",
            "chambre",
            "session",
            "legislature",
            "numero",
            unique=True,
        ),
    )

    pk = Column(Integer, primary_key=True)

    uid = Column(Text, nullable=False, unique=True)  # UID from Assemblée Nationale
    type_ = Column(Enum(TypeTexte), nullable=False)
    chambre = Column(Enum(Chambre), nullable=False)

    # Sénat only: starting year of the session (e.g. 2018 for 2018-2019)
    session = Column(Integer, nullable=True)

    # Assemblée Nationale only
    legislature = Column(Integer, nullable=True)

    numero = Column(Integer, nullable=False)
    titre_long = Column(Text, nullable=False)
    titre_court = Column(Text, nullable=False)
    date_depot = Column(Date, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    lectures = relationship("Lecture", back_populates="texte")

    __repr_keys__ = (
        "pk",
        "uid",
        "type_",
        "numero",
        "titre_long",
        "titre_court",
        "date_depot",
    )

    @classmethod
    def get(cls, uid: str) -> Optional["Texte"]:
        res: Optional["Texte"] = DBSession.query(cls).filter(cls.uid == uid).first()
        return res

    @classmethod
    def get_by_numero(
        cls, chambre: Chambre, session_or_legislature: str, numero: int
    ) -> Optional["Texte"]:
        query = DBSession.query(cls).filter(
            cls.chambre == chambre, cls.numero == numero
        )
        if chambre == Chambre.AN:
            query = query.filter_by(legislature=int(session_or_legislature))
        else:
            query = query.filter_by(session=int(session_or_legislature.split("-")[0]))
        res: Optional["Texte"] = query.first()
        return res

    @classmethod
    def exists(cls, uid: str) -> bool:
        res: bool = DBSession.query(
            DBSession.query(cls).filter(cls.uid == uid).exists()
        ).scalar()
        return res

    @classmethod
    def create(
        cls,
        uid: str,
        type_: TypeTexte,
        chambre: Chambre,
        numero: int,
        titre_long: str,
        titre_court: str,
        date_depot: datetime,
        session: Optional[int] = None,
        legislature: Optional[int] = None,
    ) -> "Texte":
        now = datetime.utcnow()
        if chambre == Chambre.AN and legislature is None:
            raise ValueError("legislature is required for AN")
        if chambre == Chambre.SENAT and session is None:
            raise ValueError("session is required for SENAT")
        texte = cls(
            uid=uid,
            type_=type_,
            chambre=chambre,
            numero=numero,
            titre_long=titre_long,
            titre_court=titre_court,
            date_depot=date_depot,
            session=session,
            legislature=legislature,
            created_at=now,
            modified_at=now,
        )
        DBSession.add(texte)
        return texte
