from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Table, Text, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import EmailType

from .base import Base, DBSession
from . import ArticleUserContentRevision


association_table = Table(
    "teams2users",
    Base.metadata,
    Column("team_pk", Integer, ForeignKey("teams.pk"), primary_key=True),
    Column("user_pk", Integer, ForeignKey("users.pk"), primary_key=True),
)


class Team(Base):
    __tablename__ = "teams"
    __repr_keys__ = ("name",)

    pk: int = Column(Integer, primary_key=True)
    name: str = Column(Text, nullable=False)
    users = relationship(
        "User", secondary="teams2users", backref=backref("teams", lazy="joined")
    )
    created_at: datetime = Column(
        DateTime, nullable=False, default=datetime.utcnow, server_default=func.now()
    )

    @classmethod
    def create(cls, name: str) -> "Team":
        team = cls(name=name)
        DBSession.add(team)
        return team

    @staticmethod
    def normalize_name(name: str) -> str:
        return name.strip()


class User(Base):
    __tablename__ = "users"
    __repr_keys__ = ("name", "email", "teams")

    pk: int = Column(Integer, primary_key=True)
    email: str = Column(EmailType, nullable=False)
    name: Optional[str] = Column(Text)
    created_at: datetime = Column(
        DateTime, nullable=False, default=datetime.utcnow, server_default=func.now()
    )
    last_login_at: Optional[datetime] = Column(DateTime)

    article_revisions: "ArticleUserContentRevision" = relationship(
        ArticleUserContentRevision, back_populates="user"
    )

    @classmethod
    def create(cls, email: str, name: Optional[str] = None) -> "User":
        user = cls(email=email, name=name)
        DBSession.add(user)
        return user

    @staticmethod
    def normalize_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def normalize_name(name: str) -> str:
        return name.strip()

    def default_name(self) -> str:
        return self.email.split("@")[0].replace(".", " ").title()

    @property
    def display_name(self):
        return self.name or self.email
