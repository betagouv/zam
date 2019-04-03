from typing import Any, Tuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from .base import Base, DBSession, log_query_with_origin  # noqa

from .amendement import Amendement, AVIS  # noqa
from .article import Article, ArticleUserContent  # noqa
from .dossier import Dossier  # noqa
from .lecture import Lecture, CHAMBRES, SESSIONS  # noqa
from .users import Team, User  # noqa
from .table import UserTable  # noqa
from .texte import Texte, TypeTexte  # noqa

from .events.base import Event  # noqa
from .events.amendement import *  # noqa
from .events.article import *  # noqa
from .events.lecture import *  # noqa


def get_one_or_create(
    model: Any, create_kwargs: Any = None, options: Any = None, **kwargs: Any
) -> Tuple[Any, bool]:
    try:
        query = DBSession.query(model).filter_by(**kwargs)
        if options is not None:
            query = query.options(options)
        return query.one(), False
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
