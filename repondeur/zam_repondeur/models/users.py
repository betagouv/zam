from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Table, Text, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import EmailType

from .base import Base, DBSession


association_table = Table(
    "teams2users",
    Base.metadata,
    Column("team_pk", Integer, ForeignKey("teams.pk"), primary_key=True),
    Column("user_pk", Integer, ForeignKey("users.pk"), primary_key=True),
)


class Team(Base):
    __tablename__ = "teams"
    __repr_keys__ = ("name",)

    pk = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    users = relationship(
        "User", secondary="teams2users", backref=backref("teams", lazy="joined")
    )
    created_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, server_default=func.now()
    )

    @classmethod
    def create(cls, name: str) -> "Team":
        team = cls(name=name)
        DBSession.add(team)
        return team


class User(Base):
    __tablename__ = "users"
    __repr_keys__ = ("name", "email", "teams")

    pk = Column(Integer, primary_key=True)
    email = Column(EmailType, nullable=False)
    name = Column(Text)
    created_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, server_default=func.now()
    )
    last_login_at = Column(DateTime)

    @classmethod
    def create(cls, email: str, name: Optional[str] = None) -> "User":
        user = cls(email=email, name=name)
        DBSession.add(user)
        return user
