from typing import Any, Dict
from datetime import date

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.clean import clean_html
from zam_repondeur.models.events.article import (
    TitreArticleModifie,
    PresentationArticleModifiee,
)
from zam_repondeur.message import Message
from zam_repondeur.resources import ArticleCollection, ArticleResource


@view_config(context=ArticleCollection, renderer="articles_list.html")
def list_articles(context: ArticleCollection, request: Request) -> Dict[str, Any]:
    return {"lecture": context.lecture_resource.model(), "articles": context.models()}


@view_config(context=ArticleResource, name="check", renderer="json")
def article_check(context: ArticleResource, request: Request) -> dict:
    article = context.model()
    timestamp = float(request.GET["since"])
    modified_amendements_at_timestamp = article.modified_amendements_at_timestamp
    modified_amendements_numbers: list = []
    if timestamp < modified_amendements_at_timestamp:
        modified_amendements_numbers = article.modified_amendements_numbers_since(
            timestamp
        )
    return {
        "modified_amendements_numbers": modified_amendements_numbers,
        "modified_at": modified_amendements_at_timestamp,
    }


@view_defaults(context=ArticleResource)
class ArticleEdit:
    def __init__(self, context: ArticleResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.article = self.context.model()

    @view_config(request_method="GET", renderer="article_edit.html")
    def get(self) -> dict:
        lecture = self.article.lecture
        return {"article": self.article, "lecture": lecture}

    @view_config(request_method="POST")
    def post(self) -> Response:
        changed = False

        new_title = self.request.POST["title"]
        if new_title != self.article.user_content.title:
            TitreArticleModifie.create(
                request=self.request, article=self.article, title=new_title
            )
            changed = True

        new_presentation = clean_html(self.request.POST["presentation"])
        if new_presentation != self.article.user_content.presentation:
            PresentationArticleModifiee.create(
                request=self.request,
                article=self.article,
                presentation=new_presentation,
            )
            changed = True

        if changed:
            self.request.session.flash(
                Message(cls="success", text="Article mis à jour avec succès.")
            )

        return HTTPFound(location=self.next_url())

    def next_url(self) -> str:
        amendements = self.context.lecture_resource["amendements"]
        url_amendements = self.request.resource_url(amendements)

        next_article = self.article.next_article
        if next_article is None:
            return url_amendements
        # Skip intersticial articles.
        while next_article.pos:
            next_article = next_article.next_article
            if next_article is None:
                return url_amendements

        resource = self.context.lecture_resource["articles"][next_article.url_key]
        return self.request.resource_url(resource)


@view_config(context=ArticleResource, name="journal", renderer="article_journal.html")
def article_journal(context: ArticleResource, request: Request) -> Dict[str, Any]:
    return {
        "lecture": context.lecture_resource.model(),
        "article": context.model(),
        "today": date.today(),
    }
