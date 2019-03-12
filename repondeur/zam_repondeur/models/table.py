from sqlalchemy import Column, ForeignKey, Integer, Index, UniqueConstraint
from sqlalchemy.orm import relationship, backref

from .amendement import Amendement
from .base import Base, DBSession
from .lecture import Lecture
from .users import User


class UserTable(Base):
    __tablename__ = "user_tables"
    __table_args__ = (
        Index("ix_user_tables__lecture_pk", "lecture_pk"),
        Index("ix_user_tables__user_pk", "user_pk"),
        UniqueConstraint("user_pk", "lecture_pk"),
    )

    pk: int = Column(Integer, primary_key=True)

    user_pk: int = Column(Integer, ForeignKey("users.pk"), nullable=False)
    user: User = relationship(User, back_populates="tables")

    lecture_pk: int = Column(Integer, ForeignKey("lectures.pk"), nullable=False)
    lecture: Lecture = relationship(
        Lecture, backref=backref("user_tables", cascade="all, delete-orphan")
    )

    amendements = relationship(
        Amendement,
        order_by=(Amendement.position, Amendement.num),
        back_populates="user_table",
    )

    __repr_keys__ = ("pk", "user_pk", "lecture_pk")

    def __lt__(self, other: "UserTable") -> bool:
        return self.user.email < other.user.email

    @classmethod
    def create(cls, user: User, lecture: Lecture) -> "UserTable":
        table = cls(user=user, lecture=lecture)
        DBSession.add(table)
        return table

    @property
    def amendements_as_string(self) -> str:
        return "_".join(str(amendement.num) for amendement in self.amendements)
