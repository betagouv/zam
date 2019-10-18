from pyramid.request import Request
from pyramid.view import view_config
from sqlalchemy.orm import joinedload, load_only, subqueryload

from zam_repondeur.models import Batch
from zam_repondeur.resources import AmendementCollection


@view_config(context=AmendementCollection, renderer="lecture_index.html")
def lecture_index(context: AmendementCollection, request: Request) -> dict:
    """
    The index lists all amendements in a lecture
    """
    lecture_resource = context.parent
    lecture = lecture_resource.model(
        subqueryload("articles").defer("content"),
        subqueryload("amendements").options(
            load_only(
                "article_pk",
                "auteur",
                "id_identique",
                "lecture_pk",
                "num",
                "parent_pk",
                "position",
                "rectif",
                "sort",
            ),
            joinedload("user_content").load_only("avis", "objet", "reponse"),
            subqueryload("location").options(
                subqueryload("batch")
                .joinedload("amendements_locations")
                .joinedload("amendement")
                .load_only("num", "rectif"),
                subqueryload("shared_table").load_only("titre"),
                subqueryload("user_table")
                .joinedload("user")
                .load_only("email", "name"),
            ),
        ),
    )
    return {
        "lecture": lecture,
        "dossier_resource": lecture_resource.dossier_resource,
        "lecture_resource": lecture_resource,
        "current_tab": "index",
        "all_amendements": lecture.amendements,
        "collapsed_amendements": Batch.collapsed_batches(lecture.amendements),
        "articles": lecture.articles,
    }
