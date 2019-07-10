from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, Integer, Text, desc
from sqlalchemy.orm import joinedload, relationship

from .base import Base, DBSession


class Dossier(Base):
    __tablename__ = "dossiers"

    pk = Column(Integer, primary_key=True)

    uid = Column(Text, nullable=False)  # the Assemblée Nationale UID
    titre = Column(Text, nullable=False)  # TODO: make it unique?
    slug: str = Column(Text, nullable=False, unique=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    lectures = relationship("Lecture", back_populates="dossier")

    __repr_keys__ = ("pk", "uid", "titre")

    @property
    def owned_by_team(self) -> None:
        return None  # TODO: transfer ownership to the whole dossier.

    @property
    def url_key(self) -> str:
        return self.slug

    @classmethod
    def all(cls) -> List["Dossier"]:
        dossiers: List["Dossier"] = (
            DBSession.query(cls)
            .options(joinedload("lectures"))
            .order_by(desc(cls.created_at))
            .all()
        )
        return dossiers

    @classmethod
    def create(cls, uid: str, titre: str, slug: str) -> "Dossier":
        now = datetime.utcnow()
        dossier = cls(uid=uid, titre=titre, slug=slug, created_at=now, modified_at=now)
        DBSession.add(dossier)
        return dossier

    @classmethod
    def get(cls, slug: str) -> Optional["Dossier"]:
        res: Optional["Dossier"] = DBSession.query(cls).filter(cls.slug == slug).first()
        return res
