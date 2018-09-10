from typing import Sequence

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.schema import MetaData
from zope.sqlalchemy import ZopeTransactionExtension


class _Base:

    __repr_keys__: Sequence[str] = tuple()

    def __repr__(self) -> str:
        if self.__repr_keys__:
            fields = "".join(
                f" {key}={getattr(self, key)!r}" for key in self.__repr_keys__
            )
            return f"<{self.__class__.__name__}{fields}>"
        else:
            return f"<{self.__class__.__name__} at 0x{id(self):x}>"


DBSession = scoped_session(
    sessionmaker(
        expire_on_commit=False,  # allow access to object attributes after commit
        extension=ZopeTransactionExtension(),  # attach to the transaction manager
    )
)
metadata = MetaData()
Base = declarative_base(cls=_Base, metadata=metadata)
