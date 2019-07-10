from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, desc
from sqlalchemy.orm import joinedload, relationship

from .base import Base, DBSession
from .users import Team


class Dossier(Base):
    __tablename__ = "dossiers"

    pk = Column(Integer, primary_key=True)

    uid = Column(Text, nullable=False)  # the Assemblée Nationale UID
    titre = Column(Text, nullable=False)  # TODO: make it unique?
    slug: str = Column(Text, nullable=False, unique=True)

    owned_by_team_pk = Column(Integer, ForeignKey("teams.pk"), nullable=True)
    owned_by_team = relationship("Team", backref="dossiers")

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    lectures = relationship("Lecture", back_populates="dossier")

    __repr_keys__ = ("pk", "slug", "titre", "uid", "owned_by_team")

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
    def create(
        cls, uid: str, titre: str, slug: str, owned_by_team: Optional[Team] = None
    ) -> "Dossier":
        now = datetime.utcnow()
        dossier = cls(
            uid=uid,
            titre=titre,
            slug=slug,
            owned_by_team=owned_by_team,
            created_at=now,
            modified_at=now,
        )
        DBSession.add(dossier)
        return dossier

    @classmethod
    def get(cls, slug: str) -> Optional["Dossier"]:
        res: Optional["Dossier"] = DBSession.query(cls).filter(cls.slug == slug).first()
        return res
