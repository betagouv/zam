from datetime import datetime
from uuid import uuid4
from typing import Any, Union

from pyramid.request import Request
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import JSONType, UUIDType

from ..base import Base, DBSession
from ..users import User


class Event(Base):
    __tablename__ = "events"

    # We use single-table inheritance, with polymorphism based on this column
    # see: https://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/inheritance.html#single-table-inheritance  # noqa
    type = Column(String(64), nullable=False)
    __mapper_args__ = {"polymorphic_identity": "event", "polymorphic_on": type}

    pk = Column(UUIDType, primary_key=True, default=uuid4)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user_pk = Column(Integer, ForeignKey("users.pk"), nullable=True)
    user = relationship(User)

    data = Column(JSONType, nullable=True)
    meta = Column(JSONType, nullable=True)

    def __init__(
        self, request: Request, meta: Union[dict, None] = None, **kwargs: Any
    ) -> None:
        if self.meta is None:
            self.meta = {}
        if request is not None:
            self.user = request.user
            self.meta["ip"] = request.remote_addr
        elif "user" in kwargs:
            self.user = kwargs.pop("user")
        if self.data is None:
            self.data = {}
        self.data.update(kwargs)
        if meta is not None:
            self.meta.update(meta)

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
