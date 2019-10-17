import inspect
import os
from typing import Any, Sequence

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.schema import MetaData
from zope.sqlalchemy import register

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))


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
        expire_on_commit=False  # allow access to object attributes after commit
    )
)
register(DBSession)

metadata = MetaData(
    # Use an explicit naming convention to help Alembic autogenerate
    naming_convention={
        "fk": "%(table_name)s_%(column_0_name)s_fkey",
        "uq": "%(table_name)s_%(column_0_N_name)s_key",
    }
)

Base = declarative_base(cls=_Base, metadata=metadata)


def log_query_with_origin(
    conn: Any,
    cursor: Any,
    statement: str,
    parameters: Any,
    context: Any,
    executemany: Any,
) -> None:
    print("\n---- SQL REQUEST ----")
    for frame in inspect.stack()[1:]:
        if frame.filename.startswith(PROJECT_ROOT):
            print(f"File {frame.filename}:{frame.lineno} in {frame.function}")
            if not frame.code_context:
                break
            for line in frame.code_context:
                print(line)
            break
    print(statement)
    print(parameters)
