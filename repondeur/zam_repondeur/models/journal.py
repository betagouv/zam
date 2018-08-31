from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from .base import Base, DBSession

KINDS = ("info", "success", "warning", "danger")


class Journal(Base):  # type: ignore
    __tablename__ = "journal"

    pk = Column(Integer, primary_key=True)
    kind = Column(Text)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    lecture_pk = Column(Integer, ForeignKey("lectures.pk"))
    lecture = relationship("Lecture", back_populates="journal")

    @classmethod
    def create(cls, lecture, kind: str, message: str) -> "Journal":  # type: ignore
        if kind not in KINDS:
            raise Exception(
                f"Kind of journal message not supported, must be one of {KINDS}."
            )
        journal = cls(lecture=lecture, kind=kind, message=message)
        DBSession.add(journal)
        return journal

    @property
    def created_at_timestamp(self) -> float:
        timestamp: float = (self.created_at - datetime(1970, 1, 1)).total_seconds()
        return timestamp
