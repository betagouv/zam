from datetime import datetime
from typing import Optional
import enum

from sqlalchemy import Column, Date, DateTime, Enum, Integer, Text
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


class Texte(Base):
    __tablename__ = "textes"

    pk = Column(Integer, primary_key=True)

    uid = Column(Text, nullable=False)
    type_ = Column(Enum(TypeTexte), nullable=False)
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
    def get_by_numero(cls, numero: int) -> Optional["Texte"]:
        res: Optional["Texte"] = DBSession.query(cls).filter(
            cls.numero == numero
        ).first()
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
        type_: str,
        numero: int,
        titre_long: str,
        titre_court: str,
        date_depot: datetime,
    ) -> "Texte":
        now = datetime.utcnow()
        texte = cls(
            uid=uid,
            type_=type_,
            numero=numero,
            titre_long=titre_long,
            titre_court=titre_court,
            date_depot=date_depot,
            created_at=now,
            modified_at=now,
        )
        DBSession.add(texte)
        return texte
