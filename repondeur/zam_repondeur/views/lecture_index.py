from typing import Callable, Tuple

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.orm import joinedload, load_only, subqueryload

from zam_repondeur.models import (
    Amendement,
    AmendementList,
    Article,
    Batch,
    Chambre,
    DBSession,
)
from zam_repondeur.resources import AmendementCollection, LectureResource

AMDTS_OPTIONS = [
    load_only(
        "article_pk",
        "auteur",
        "id_identique",
        "lecture_pk",
        "mission_titre",
        "mission_titre_court",
        "num",
        "parent_pk",
        "position",
        "rectif",
        "sort",
    ),
    joinedload("user_content").load_only(
        "avis", "has_reponse", "objet", "reponse_hash"
    ),
    joinedload("location").options(
        subqueryload("batch")
        .joinedload("amendements_locations")
        .joinedload("amendement")
        .load_only("num", "rectif"),
        subqueryload("shared_table").load_only("titre"),
        subqueryload("user_table").joinedload("user").load_only("email", "name"),
    ),
    (
        subqueryload("identiques")
        .load_only("num")
        .joinedload("user_content")
        .load_only("reponse_hash")
    ),
]


@view_config(context=LectureResource)
def default_view(context: LectureResource, request: Request) -> Response:
    return HTTPFound(location=request.resource_url(context["amendements"]))


@view_config(context=AmendementCollection, renderer="lecture_index.html")
def lecture_index(context: AmendementCollection, request: Request) -> dict:
    """
    The index lists all amendements for small lectures, only by article for big ones.
    """
    lecture_resource = context.parent
    lecture = lecture_resource.model(subqueryload("articles").defer("content"))
    total_count_amendements = lecture.nb_amendements
    max_amendements_for_full_index = int(
        request.registry.settings.get("zam.limits.max_amendements_for_full_index", 1000)
    )
    too_many_amendements = total_count_amendements > max_amendements_for_full_index
    default_param = "article.1.." if too_many_amendements else "all"
    article_param = request.params.get("article", default_param)
    if article_param == "all":
        amendements = (
            DBSession.query(Amendement)
            .join(Article)
            .filter(Amendement.lecture == lecture,)
            .options(*AMDTS_OPTIONS)
        )
    else:
        article_type, article_num, article_mult, article_pos = article_param.split(".")
        amendements = (
            DBSession.query(Amendement)
            .join(Article)
            .filter(
                Article.pk == Amendement.article_pk,
                Amendement.lecture == lecture,
                Article.type == article_type,
                Article.num == article_num,
                Article.mult == article_mult,
                Article.pos == article_pos,
            )
            .options(*AMDTS_OPTIONS)
        )

    amendements = AmendementList(amendements, sort_key=get_sort_key(request))
    article_count_amendements = len(amendements)
    return {
        "lecture": lecture,
        "dossier_resource": lecture_resource.dossier_resource,
        "lecture_resource": lecture_resource,
        "current_tab": "index",
        "total_count_amendements": total_count_amendements,
        "article_count_amendements": article_count_amendements,
        "amendements": amendements,
        "collapsed_amendements": Batch.collapsed_batches(amendements),
        "articles": lecture.articles,
        "article_param": article_param,
        "progress_url": request.resource_url(lecture_resource, "progress_status"),
        "progress_interval": request.registry.settings["zam.progress.lecture_refresh"],
        "too_many_amendements": too_many_amendements,
        "enter_amendement_url": request.resource_url(context, "saisie"),
        "show_help": lecture.chambre in {Chambre.AN, Chambre.SENAT},
    }


def get_sort_key(request: Request) -> Callable[[Amendement], tuple]:
    """
    Add flag in query params to enable alternate sorting
    """

    try:
        tri_amendement_enabled = int(request.params.get("tri_amendement", "0"))
    except ValueError:
        tri_amendement_enabled = 0

    return sort_by_tri_amendement if tri_amendement_enabled else sort_by_position


def sort_by_tri_amendement(amendement: Amendement) -> Tuple[bool, str, Article, str]:
    return (
        amendement.is_abandoned,
        amendement.tri_amendement or "~",
        amendement.article,
        amendement.num,
    )


def sort_by_position(amendement: Amendement) -> Tuple[bool, int, Article, str]:
    return amendement.sort_key
