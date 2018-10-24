from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.orm import joinedload

from zam_repondeur.resources import ArticleResource


@view_config(context=ArticleResource, name="reponses", renderer="visionneuse.html")
def list_reponses(context: ArticleResource, request: Request) -> Response:
    article = context.model(joinedload("lecture"), joinedload("amendements"))
    lecture = article.lecture
    check_url = request.resource_path(context.parent.parent, "check")
    return {
        "lecture": lecture,
        "timestamp": lecture.modified_at_timestamp,
        "check_url": check_url,
        "article": article,
        "next_article": article.next_article,
        "previous_article": article.previous_article,
    }
