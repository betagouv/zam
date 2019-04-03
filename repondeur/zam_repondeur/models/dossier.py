from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy.orm import relationship

from .base import Base, DBSession


class Dossier(Base):
    __tablename__ = "dossiers"

    pk = Column(Integer, primary_key=True)

    uid = Column(Text, nullable=False)  # the Assemblée Nationale UID
    titre = Column(Text, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    lectures = relationship("Lecture", back_populates="dossier")

    __repr_keys__ = ("pk", "uid", "titre")

    @classmethod
    def get(cls, uid: str) -> Optional["Dossier"]:
        res: Optional["Dossier"] = DBSession.query(cls).filter(cls.uid == uid).first()
        return res

    @classmethod
    def exists(cls, uid: str) -> bool:
        res: bool = DBSession.query(
            DBSession.query(cls).filter(cls.uid == uid).exists()
        ).scalar()
        return res

    @classmethod
    def create(cls, uid: str, titre: str) -> "Dossier":
        now = datetime.utcnow()
        dossier = cls(uid=uid, titre=titre, created_at=now, modified_at=now)
        DBSession.add(dossier)
        return dossier
