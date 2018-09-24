from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

from zam_repondeur.resources import ArticleResource


@view_config(context=ArticleResource, name="reponses", renderer="visionneuse.html")
def list_reponses(context: ArticleResource, request: Request) -> Response:
    article = context.model()
    lecture = article.lecture
    check_url = request.resource_path(context.parent.parent, "check")
    return {
        "dossier_legislatif": lecture.dossier_legislatif,
        "lecture": str(lecture),
        "articles": lecture.articles,
        "timestamp": lecture.modified_at_timestamp,
        "check_url": check_url,
        "current_article": article,
    }
