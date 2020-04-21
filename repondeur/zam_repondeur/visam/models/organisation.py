from typing import Optional

from sqlalchemy import Column, Integer, Text

from zam_repondeur.models.base import Base, DBSession


class Organisation(Base):
    __tablename__ = "organisations"

    __repr_keys__ = ("name",)

    pk = Column(Integer, primary_key=True)
    name: str = Column(Text, nullable=False, unique=True)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def create(cls, name: str) -> "Organisation":
        organisation = cls(name=name)
        DBSession.add(organisation)
        return organisation

    @property
    def is_gouvernement(self) -> bool:
        return self.name == "Gouvernement"

    @classmethod
    def find_by_name(cls, name: str) -> Optional["Organisation"]:
        organisation: Optional[Organisation] = DBSession.query(cls).filter_by(
            name=name
        ).one_or_none()
        return organisation
