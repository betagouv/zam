from typing import Any, Tuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from .base import Base, DBSession, log_query_with_origin  # noqa

from .amendement import Amendement, AVIS  # noqa
from .article import Article, ArticleUserContent, ArticleUserContentRevision  # noqa
from .journal import Journal  # noqa
from .lecture import Lecture, CHAMBRES, SESSIONS  # noqa
from .users import Team, User  # noqa


def get_one_or_create(
    model: Any, create_kwargs: Any = None, **kwargs: Any
) -> Tuple[Any, bool]:
    try:
        return DBSession.query(model).filter_by(**kwargs).one(), False
    except NoResultFound:
        kwargs.update(create_kwargs or {})
        try:
            with DBSession.begin_nested():
                created = model.create(**kwargs)
                DBSession.add(created)
            return created, True
        except IntegrityError:  # Race condition.
            try:
                return DBSession.query(model).filter_by(**kwargs).one(), False
            except NoResultFound:  # Retry to raise the appropriated IntegrityError.
                with DBSession.begin_nested():
                    created = model.create(**kwargs)
                    DBSession.add(created)
                return created, True
