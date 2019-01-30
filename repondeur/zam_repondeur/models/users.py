from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, Text, func
from sqlalchemy_utils import EmailType

from .base import Base, DBSession


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
