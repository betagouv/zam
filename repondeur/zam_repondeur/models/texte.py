from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy.orm import relationship

from .base import Base, DBSession


class Texte(Base):
    __tablename__ = "textes"

    pk = Column(Integer, primary_key=True)

    uid = Column(Text)
    type_ = Column(Text)
    numero = Column(Integer)
    titre_long = Column(Text)
    titre_court = Column(Text)
    date_depot = Column(DateTime)

    lectures = relationship("Lecture", back_populates="texte")

    created_at = Column(DateTime)
    modified_at = Column(DateTime)

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
