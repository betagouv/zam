from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.orm import joinedload, lazyload, load_only, subqueryload

from zam_repondeur.resources import ArticleResource


@view_config(context=ArticleResource, name="reponses", renderer="visionneuse.html")
def list_reponses(context: ArticleResource, request: Request) -> Response:
    article = context.model(
        lazyload("amendements").options(
            load_only(
                "article_pk",
                "auteur",
                "corps",
                "expose",
                "groupe",
                "lecture_pk",
                "num",
                "parent_pk",
                "rectif",
                "sort",
            ),
            joinedload("user_content").load_only("avis", "objet", "reponse"),
        ),
        lazyload("lecture").options(
            lazyload("amendements").options(
                load_only("article_pk", "auteur", "num", "rectif", "sort"),
                joinedload("user_content").load_only("avis"),
            ),
            joinedload("texte").load_only("legislature", "numero"),
            lazyload("articles").options(
                load_only("lecture_pk", "mult", "num", "pos", "type"),
                subqueryload("amendements"),
            ),
        ),
    )
    return {
        "lecture": article.lecture,
        "article": article,
        "grouped_displayable_amendements": list(
            article.grouped_displayable_amendements()
        ),
        "next_article": article.next_displayable_article,
        "previous_article": article.previous_displayable_article,
    }
