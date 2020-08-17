from pyramid.request import Request
from pyramid.view import view_config

from zam_repondeur.resources import ArticleResource


@view_config(
    context=ArticleResource,
    name="preview",
    request_method="GET",
    renderer="article_preview.html",
)
def preview_article(context: ArticleResource, request: Request) -> dict:
    return {
        "article": context.model(),
    }
