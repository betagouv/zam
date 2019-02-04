from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .amendement import Amendement
from .base import Base
from .users import User


class UserTable(Base):
    __tablename__ = "user_tables"

    pk: int = Column(Integer, primary_key=True)

    user_pk: int = Column(Integer, ForeignKey("users.pk"))
    user: User = relationship(User, back_populates="table")

    amendements = relationship(
        Amendement,
        order_by=(Amendement.position, Amendement.num),
        back_populates="user_table",
    )

    __repr_keys__ = ("pk", "user_pk")
