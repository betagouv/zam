from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Table, Text, func
from sqlalchemy.orm import relationship, backref, joinedload
from sqlalchemy_utils import EmailType

from zam_repondeur.users import get_last_activity_time, set_last_activity_time
from .base import Base, DBSession

# Make these types available to mypy, but avoid circular imports
if TYPE_CHECKING:
    from .lecture import Lecture  # noqa
    from .table import UserTable  # noqa


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

    def everyone_but_me(self, me: "User") -> List["User"]:
        return [user for user in self.users if user is not me]


class User(Base):
    __tablename__ = "users"
    __repr_keys__ = ("name", "email", "teams")

    INACTIVE_AFTER = 30  # minutes.

    pk: int = Column(Integer, primary_key=True)
    email: str = Column(EmailType, nullable=False, unique=True)
    name: Optional[str] = Column(Text)
    created_at: datetime = Column(
        DateTime, nullable=False, default=datetime.utcnow, server_default=func.now()
    )
    last_login_at: Optional[datetime] = Column(DateTime)

    tables = relationship("UserTable", back_populates="user")

    def __str__(self) -> str:
        if self.name:
            return f"{self.name} ({self.email})"
        else:
            return self.email

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
    def display_name(self) -> str:
        return self.name or self.email

    @property
    def last_activity(self) -> Optional[datetime]:
        return get_last_activity_time(self.email)

    def record_activity(self) -> None:
        set_last_activity_time(self.email)

    @property
    def is_active(self) -> bool:
        if self.last_activity is None:
            return False
        elapsed = (datetime.utcnow() - self.last_activity).total_seconds()
        return elapsed < self.INACTIVE_AFTER * 60

    def table_for(self, lecture: "Lecture") -> "UserTable":
        from . import get_one_or_create
        from .table import UserTable

        table: UserTable
        table, _ = get_one_or_create(
            UserTable,
            user=self,
            lecture=lecture,
            options=joinedload("amendements").joinedload("article"),
        )
        return table

    @classmethod
    def everyone_but_me(self, me: "User") -> List["User"]:
        users: List["User"] = DBSession.query(User).filter(User.email != me.email).all()
        return users
