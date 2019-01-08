from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from .base import Base, DBSession


association_table = Table(
    "teams2users",
    Base.metadata,
    Column("teams_pk", Integer, ForeignKey("teams.pk")),
    Column("users_pk", Integer, ForeignKey("users.pk")),
)


class Team(Base):
    __tablename__ = "teams"
    __repr_keys__ = ("name",)

    pk = Column(Integer, primary_key=True)
    name = Column(Text)
    users = relationship("User", secondary="teams2users", backref="teams")
    created_at = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, name: str) -> "Team":
        team = cls(name=name)
        DBSession.add(team)
        return team


class User(Base):
    __tablename__ = "users"
    __repr_keys__ = ("name", "email", "teams")

    pk = Column(Integer, primary_key=True)
    email = Column(String(254))
    name = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, name: str, email: str) -> "User":
        user = cls(name=name, email=email)
        DBSession.add(user)
        return user
