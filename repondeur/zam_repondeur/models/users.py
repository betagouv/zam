from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Column, DateTime, Integer, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType

from .base import Base, DBSession

# Make these types available to mypy, but avoid circular imports
if TYPE_CHECKING:
    from .lecture import Lecture  # noqa
    from .table import UserTable  # noqa


class User(Base):
    __tablename__ = "users"
    __repr_keys__ = ("name", "email")

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

    def table_for(self, lecture: "Lecture") -> "UserTable":
        from . import get_one_or_create
        from .table import UserTable

        table: UserTable
        table, _ = get_one_or_create(UserTable, user=self, lecture=lecture)
        return table
