from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import Column, DateTime, Integer, Text, desc
from sqlalchemy.orm import joinedload, relationship

from .base import Base, DBSession
from .events.base import LastEventMixin


class Dossier(Base, LastEventMixin):
    __tablename__ = "dossiers"

    pk = Column(Integer, primary_key=True)

    uid = Column(Text, nullable=False, unique=True)  # the Assemblée Nationale UID
    titre = Column(Text, nullable=False)  # TODO: make it unique?
    slug: str = Column(Text, nullable=False, unique=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    team = relationship("Team", uselist=False, back_populates="dossier")
    lectures = relationship(
        "Lecture", back_populates="dossier", cascade="all, delete-orphan"
    )

    events = relationship(
        "Event",
        order_by="Event.created_at.desc()",
        cascade="all, delete-orphan",
        backref="dossier",
    )

    __repr_keys__ = ("pk", "slug", "titre", "uid", "team")

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
        base_slug = slug
        counter = 1
        while True:
            if counter > 1:
                slug = f"{base_slug}-{counter}"
            existing = DBSession.query(cls).filter_by(slug=slug).first()
            if existing is None:
                break
            counter += 1
        dossier = cls(uid=uid, titre=titre, slug=slug, created_at=now, modified_at=now)
        DBSession.add(dossier)
        return dossier

    @classmethod
    def get(cls, slug: str, *options: Any) -> Optional["Dossier"]:
        res: Optional["Dossier"] = DBSession.query(cls).filter(
            cls.slug == slug
        ).options(*options).first()
        return res

    @classmethod
    def exists(cls, slug: str) -> bool:
        res: bool = DBSession.query(
            DBSession.query(cls).filter(cls.slug == slug).exists()
        ).scalar()

        return res
