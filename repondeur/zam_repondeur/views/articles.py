from datetime import date
from typing import Any, Dict

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.message import Message
from zam_repondeur.models.events.article import (
    PresentationArticleModifiee,
    TitreArticleModifie,
)
from zam_repondeur.resources import ArticleResource
from zam_repondeur.services.clean import clean_all_html, clean_html


@view_defaults(context=ArticleResource)
class ArticleEdit:
    def __init__(self, context: ArticleResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.article = self.context.model()

    @view_config(request_method="GET", renderer="article_edit.html")
    def get(self) -> dict:
        lecture = self.article.lecture
        return {
            "article": self.article,
            "lecture": lecture,
            "lecture_resource": self.context.lecture_resource,
            "dossier_resource": self.context.lecture_resource.dossier_resource,
            "current_tab": "article",
            "back_url": self.back_url(),
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        changed = False

        new_title = clean_all_html(self.request.POST["title"])
        if new_title != self.article.user_content.title:
            TitreArticleModifie.create(
                article=self.article, title=new_title, request=self.request
            )
            changed = True

        new_presentation = clean_html(self.request.POST["presentation"])
        if new_presentation != self.article.user_content.presentation:
            PresentationArticleModifiee.create(
                article=self.article,
                presentation=new_presentation,
                request=self.request,
            )
            changed = True

        if changed:
            self.request.session.flash(
                Message(cls="success", text="Article mis à jour avec succès.")
            )

        return HTTPFound(location=self.next_url())

    def back_url(self) -> str:
        amendements_collection = self.context.lecture_resource["amendements"]
        return self.request.resource_url(amendements_collection)

    def next_url(self) -> str:
        next_article = self.article.next_article
        if next_article is None:
            return self.back_url()

        # Skip intersticial articles.
        while next_article.pos:
            next_article = next_article.next_article
            if next_article is None:
                return self.back_url()

        return self.request.resource_url(self.context.parent[next_article.url_key])


@view_config(context=ArticleResource, name="journal", renderer="article_journal.html")
def article_journal(context: ArticleResource, request: Request) -> Dict[str, Any]:
    return {
        "lecture": context.lecture_resource.model(),
        "lecture_resource": context.lecture_resource,
        "dossier_resource": context.lecture_resource.dossier_resource,
        "current_tab": "article",
        "article": context.model(),
        "today": date.today(),
        "back_url": request.resource_url(context),
    }
