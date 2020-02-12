from typing import Any, Tuple

from pyramid_retry import mark_error_retryable
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from .amendement import AVIS, Amendement, AmendementList  # noqa
from .article import Article, ArticleUserContent  # noqa
from .base import Base, DBSession, log_query_with_origin  # noqa
from .batch import Batch  # noqa
from .chambre import Chambre  # noqa
from .dossier import Dossier  # noqa
from .events.amendement import (  # noqa
    AmendementIrrecevable,
    AmendementRectifie,
    AmendementTransfere,
    AvisAmendementModifie,
    BatchSet,
    BatchUnset,
    CommentsAmendementModifie,
    CorpsAmendementModifie,
    ExposeAmendementModifie,
    ObjetAmendementModifie,
    ReponseAmendementModifiee,
)
from .events.article import (  # noqa
    ContenuArticleModifie,
    PresentationArticleModifiee,
    TitreArticleModifie,
)
from .events.base import Event  # noqa
from .events.lecture import (  # noqa
    AmendementsAJour,
    AmendementsNonRecuperes,
    AmendementsNonTrouves,
    AmendementsRecuperes,
    AmendementsRecuperesLiasse,
    ArticlesRecuperes,
    LectureCreee,
    ReponsesImportees,
    ReponsesImporteesJSON,
    SharedTableCreee,
    SharedTableRenommee,
    SharedTableSupprimee,
)
from .lecture import Lecture  # noqa
from .phase import Phase  # noqa
from .table import SharedTable, UserTable  # noqa
from .texte import Texte, TypeTexte  # noqa
from .users import AllowedEmailPattern, Team, User  # noqa

mark_error_retryable(IntegrityError)


def _get_one(model: Any, options: Any = None, **kwargs: Any) -> Tuple[Any, bool]:
    query = DBSession.query(model).filter_by(**kwargs)
    if options is not None:
        query = query.options(options)
    return query.one(), False


def _create(model: Any, create_kwargs: Any = None, **kwargs: Any) -> Tuple[Any, bool]:
    kwargs.update(create_kwargs or {})
    created = model.create(**kwargs)
    return created, True


def get_one_or_create(
    model: Any, create_kwargs: Any = None, options: Any = None, **kwargs: Any
) -> Tuple[Any, bool]:
    try:
        return _get_one(model, options, **kwargs)
    except NoResultFound:
        return _create(model, create_kwargs, **kwargs)
