from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.orm import joinedload

from zam_repondeur.resources import ArticleResource


@view_config(context=ArticleResource, name="reponses", renderer="visionneuse.html")
def list_reponses(context: ArticleResource, request: Request) -> Response:
    article = context.model(joinedload("lecture"), joinedload("amendements"))
    check_url = request.resource_path(context, "check")
    return {
        "lecture": article.lecture,
        "timestamp": article.modified_amendements_at_timestamp,
        "check_url": check_url,
        "article": article,
        "grouped_displayable_amendements": list(
            article.grouped_displayable_amendements()
        ),
        "next_article": article.next_displayable_article,
        "previous_article": article.previous_displayable_article,
    }
