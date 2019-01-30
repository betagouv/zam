from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType

from .base import Base, DBSession
from .amendement import Amendement


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

    user_space = relationship(
        "UserSpace", back_populates="user", uselist=False, lazy="joined"
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
    def display_name(self) -> str:
        return self.name or self.email


class UserSpace(Base):
    __tablename__ = "user_spaces"

    pk: int = Column(Integer, primary_key=True)

    user_pk: int = Column(Integer, ForeignKey("users.pk"))
    user: User = relationship(User, back_populates="user_space")

    amendements = relationship(
        Amendement,
        order_by=(Amendement.position, Amendement.num),
        back_populates="user_space",
    )

    __repr_keys__ = ("pk", "user_pk")
