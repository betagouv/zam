from copy import deepcopy
from typing import Any, Tuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from .base import Base, DBSession, log_query_with_origin  # noqa

from .amendement import Amendement, Batch, AVIS  # noqa
from .article import Article, ArticleUserContent  # noqa
from .dossier import Dossier  # noqa
from .lecture import Lecture, CHAMBRES, SESSIONS  # noqa
from .users import Team, User  # noqa
from .table import UserTable  # noqa
from .texte import Chambre, Texte, TypeTexte  # noqa

from .events.base import Event  # noqa
from .events.amendement import *  # noqa
from .events.article import *  # noqa
from .events.lecture import *  # noqa


def _get_one(model: Any, options: Any = None, **kwargs: Any) -> Tuple[Any, bool]:
    query = DBSession.query(model).filter_by(**kwargs)
    if options is not None:
        query = query.options(options)
    return query.one(), False


def _create(model: Any, create_kwargs: Any = None, **kwargs: Any) -> Tuple[Any, bool]:
    kwargs = deepcopy(kwargs)  # Otherwise updated in place for all subsequent queries.
    kwargs.update(create_kwargs or {})
    with DBSession.begin_nested():
        created = model.create(**kwargs)
        DBSession.add(created)
    return created, True


def get_one_or_create(
    model: Any, create_kwargs: Any = None, options: Any = None, **kwargs: Any
) -> Tuple[Any, bool]:
    try:
        return _get_one(model, options, **kwargs)
    except NoResultFound:
        try:
            return _create(model, create_kwargs, **kwargs)
        except IntegrityError:  # Race condition.
            try:
                return _get_one(model, options, **kwargs)
            except NoResultFound:  # Retry to raise the appropriated IntegrityError.
                return _create(model, create_kwargs, **kwargs)
