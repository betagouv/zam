from typing import Any, Tuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from .base import Base, DBSession  # noqa

from .amendement import Amendement, AVIS  # noqa
from .article import Article  # noqa
from .lecture import Lecture, CHAMBRES, SESSIONS  # noqa


def get_one_or_create(
    db_session: DBSession,
    model: Any,
    create_method: str = "",
    create_method_kwargs: Any = None,
    **kwargs: dict
) -> Tuple[Any, bool]:
    try:
        return db_session.query(model).filter_by(**kwargs).one(), False
    except NoResultFound:
        kwargs.update(create_method_kwargs or {})
        try:
            with db_session.begin_nested():
                created = getattr(model, create_method, model)(**kwargs)
                db_session.add(created)
            return created, True
        except IntegrityError:
            return db_session.query(model).filter_by(**kwargs).one(), False
