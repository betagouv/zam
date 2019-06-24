from typing import Any, Tuple

from pyramid_retry import mark_error_retryable
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from .base import Base, DBSession, log_query_with_origin  # noqa

from .amendement import Amendement, Batch, Mission, AVIS  # noqa
from .article import Article, ArticleUserContent  # noqa
from .chambre import Chambre  # noqa
from .dossier import Dossier  # noqa
from .lecture import Lecture  # noqa
from .users import Team, User  # noqa
from .table import UserTable  # noqa
from .texte import Texte, TypeTexte  # noqa

from .events.base import Event  # noqa
from .events.amendement import (  # noqa
    AmendementRectifie,
    AmendementIrrecevable,
    AmendementTransfere,
    CorpsAmendementModifie,
    ExposeAmendementModifie,
    AvisAmendementModifie,
    ObjetAmendementModifie,
    ReponseAmendementModifiee,
    CommentsAmendementModifie,
    BatchSet,
    BatchUnset,
)
from .events.article import (  # noqa
    ContenuArticleModifie,
    TitreArticleModifie,
    PresentationArticleModifiee,
)
from .events.lecture import (  # noqa
    LectureCreee,
    ArticlesRecuperes,
    AmendementsRecuperes,
    AmendementsRecuperesLiasse,
    AmendementsNonRecuperes,
    AmendementsAJour,
    AmendementsNonTrouves,
    ReponsesImportees,
    ReponsesImporteesJSON,
)


mark_error_retryable(IntegrityError)


def _get_one(model: Any, options: Any = None, **kwargs: Any) -> Tuple[Any, bool]:
    query = DBSession.query(model).filter_by(**kwargs)
    if options is not None:
        query = query.options(options)
    return query.one(), False


def _create(model: Any, create_kwargs: Any = None, **kwargs: Any) -> Tuple[Any, bool]:
    kwargs.update(create_kwargs or {})
    with DBSession.begin_nested():  # unnecessary?
        created = model.create(**kwargs)
        DBSession.add(created)
    return created, True


def get_one_or_create(
    model: Any, create_kwargs: Any = None, options: Any = None, **kwargs: Any
) -> Tuple[Any, bool]:
    try:
        return _get_one(model, options, **kwargs)
    except NoResultFound:
        return _create(model, create_kwargs, **kwargs)
