from typing import Any, Dict

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.clean import clean_html
from zam_repondeur.message import Message
from zam_repondeur.resources import ArticleCollection, ArticleResource


@view_config(
    context=ArticleCollection, request_method="GET", renderer="articles_list.html"
)
def list_articles(context: ArticleCollection, request: Request) -> Dict[str, Any]:
    return {"lecture": context.lecture_resource.model(), "articles": context.models()}


@view_defaults(context=ArticleResource)
class ArticleEdit:
    def __init__(self, context: ArticleResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.article = self.context.model()

    @view_config(request_method="GET", renderer="article_edit.html")
    def get(self) -> dict:
        lecture = self.context.lecture_resource.model()
        return {"article": self.article, "lecture": lecture}

    @view_config(request_method="POST")
    def post(self) -> Response:
        self.article.titre = self.request.POST["titre"]
        self.article.jaune = clean_html(self.request.POST["jaune"])
        self.request.session.flash(
            Message(cls="success", text="Article mis à jour avec succès.")
        )
        next_article = self.article.next_article
        if next_article:
            resource = self.context.lecture_resource["articles"]
            location = self.request.resource_url(resource, next_article.url_key)
        else:
            resource = self.context.lecture_resource["amendements"]
            location = self.request.resource_url(resource)
        return HTTPFound(location=location)
