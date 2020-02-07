from pyramid.request import Request
from pyramid.view import view_config
from sqlalchemy.orm import joinedload, load_only, subqueryload

from zam_repondeur.models import Amendement, AmendementList, Article, Batch, DBSession
from zam_repondeur.resources import AmendementCollection


@view_config(context=AmendementCollection, renderer="lecture_index.html")
def lecture_index(context: AmendementCollection, request: Request) -> dict:
    """
    The index lists all amendements in a lecture
    """
    lecture_resource = context.parent
    article_param = request.params.get("article", "article.1..")
    article_type, article_num, article_mult, article_pos = article_param.split(".")
    lecture = lecture_resource.model(subqueryload("articles").defer("content"))
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
        .options(
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
                subqueryload("user_table")
                .joinedload("user")
                .load_only("email", "name"),
            ),
        )
    )
    amendements = AmendementList(amendements)
    total_count_amendements = lecture.nb_amendements
    return {
        "lecture": lecture,
        "dossier_resource": lecture_resource.dossier_resource,
        "lecture_resource": lecture_resource,
        "current_tab": "index",
        "total_count_amendements": total_count_amendements,
        "article_count_amendements": len(amendements),
        "amendements": amendements,
        "collapsed_amendements": Batch.collapsed_batches(amendements),
        "articles": lecture.articles,
        "article_param": article_param,
        "progress_url": request.resource_url(lecture_resource, "progress_status"),
    }
