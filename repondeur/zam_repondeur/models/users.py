from datetime import datetime
from fnmatch import fnmatchcase
from typing import TYPE_CHECKING, Any, List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Table, Text, func
from sqlalchemy.orm import backref, relationship
from sqlalchemy_utils import EmailType

from zam_repondeur.services.users import repository as users_repository

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
    name: str = Column(Text, nullable=False, unique=True)

    dossier_pk = Column(Integer, ForeignKey("dossiers.pk"))
    dossier = relationship("Dossier", back_populates="team")
    users = relationship("User", secondary="teams2users", backref=backref("teams"))
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
    admin_at: Optional[datetime] = Column(DateTime)

    tables = relationship("UserTable", back_populates="user")

    def __str__(self) -> str:
        if self.name:
            return f"{self.name} ({self.email})"
        else:
            return self.email

    @classmethod
    def create(
        cls, email: str, name: Optional[str] = None, admin_at: Optional[DateTime] = None
    ) -> "User":
        user = cls(email=email, name=name, admin_at=admin_at)
        DBSession.add(user)
        return user

    @staticmethod
    def normalize_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def email_is_well_formed(email: str) -> bool:
        return email != "" and "@" in email

    @staticmethod
    def email_is_allowed(email: str) -> bool:
        patterns = DBSession.query(AllowedEmailPattern).all()
        return any(pattern.is_allowed(email) for pattern in patterns)

    @staticmethod
    def normalize_name(name: str) -> str:
        return name.strip()

    def default_name(self) -> str:
        return self.email.split("@")[0].replace(".", " ").title()

    @property
    def is_admin(self) -> bool:
        return bool(self.admin_at)

    @property
    def last_activity(self) -> Optional[datetime]:
        return users_repository.get_last_activity_time(self.email)

    def record_activity(self) -> None:
        users_repository.set_last_activity_time(self.email)

    @property
    def is_active(self) -> bool:
        if self.last_activity is None:
            return False
        elapsed = (datetime.utcnow() - self.last_activity).total_seconds()
        return elapsed < self.INACTIVE_AFTER * 60

    def table_for(self, lecture: "Lecture", options: Any = None) -> "UserTable":
        from . import get_one_or_create
        from .table import UserTable

        table: UserTable
        table, _ = get_one_or_create(
            UserTable, user=self, lecture=lecture, options=options
        )
        return table

    @classmethod
    def everyone_but_me(self, me: "User") -> List["User"]:
        users: List["User"] = DBSession.query(User).filter(User.email != me.email).all()
        return users


class AllowedEmailPattern(Base):
    """
    Only e-mail addresses that match one of these patterns are allowed to use the app
    """

    __tablename__ = "allowed_email_patterns"

    pk: int = Column(Integer, primary_key=True)
    created_at: datetime = Column(
        DateTime, nullable=False, default=datetime.utcnow, server_default=func.now()
    )

    pattern: str = Column(
        Text,
        nullable=False,
        unique=True,
        doc="A glob-style pattern that matches allowed email addresses",
    )
    comment: str = Column(
        Text,
        nullable=True,
        doc="A user-defined comment to keep track of why we added this pattern",
    )

    def __str__(self) -> str:
        comment = f" ({self.comment})" if self.comment else ""
        return f"{self.pattern}{comment}"

    @classmethod
    def create(
        cls, pattern: str, comment: Optional[str] = None
    ) -> "AllowedEmailPattern":
        instance = cls(pattern=pattern, comment=comment)
        DBSession.add(instance)
        return instance

    def is_allowed(self, email: str) -> bool:
        """
        Check if an e-mail address is allowed by this pattern
        """
        return fnmatchcase(email, self.pattern)
