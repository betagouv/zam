from datetime import datetime
from typing import Any

from pyramid.request import Request
from pyramid.threadlocal import get_current_request
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from sqlalchemy_utils import JSONType

# from sqlalchemy_utils import UUIDType

from ..models.base import Base, DBSession
from ..models.users import User


class Event(Base):
    __tablename__ = "events"

    # We use single-table inheritance, with polymorphism based on this column
    # see: https://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/inheritance.html#single-table-inheritance  # noqa
    type = Column(String(64), nullable=False)
    __mapper_args__ = {"polymorphic_identity": "event", "polymorphic_on": type}

    pk = Column(Integer, primary_key=True)
    # pk = Column(UUIDType, primary_key=True)

    created_at = Column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )

    user_pk = Column(Integer, ForeignKey("users.pk"), nullable=True)
    user = relationship(User)

    data = Column(JSONType, nullable=True)

    def __init__(self, request: Request = None, **kwargs: Any) -> None:
        request = request or get_current_request()
        if request is not None:
            self.user = request.user
        if self.data is None:
            self.data = {}
        self.data.update(kwargs)

    @property
    def created_at_timestamp(self) -> float:
        timestamp: float = (self.created_at - datetime(1970, 1, 1)).total_seconds()
        return timestamp

    def apply(self) -> None:
        raise NotImplementedError

    @classmethod
    def create(cls, *args: Any, **kwargs: Any) -> "Event":
        event = cls(*args, **kwargs)
        event.apply()
        DBSession.add(event)
        return event
