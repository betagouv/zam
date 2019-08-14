from typing import Any, Dict, Tuple
from datetime import date

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.clean import clean_html
from zam_repondeur.models import Article
from zam_repondeur.models.article import mult_key
from zam_repondeur.models.events.article import (
    TitreArticleModifie,
    PresentationArticleModifiee,
)
from zam_repondeur.message import Message
from zam_repondeur.resources import ArticleCollection, ArticleResource


@view_config(context=ArticleCollection, renderer="articles_list.html")
def list_articles(context: ArticleCollection, request: Request) -> Dict[str, Any]:
    def _sort_key(item: Article) -> Tuple[int, str, Tuple[int, str], int]:
        """Custom sort: we want link related to `Titre` to be at the very end.

        This is because it is the correct order in the derouleur and thus
        it is discussed at the end of the seance.
        """
        return (
            Article._ORDER_TYPE[""]
            if item.type == "titre"
            else Article._ORDER_TYPE[item.type or ""],
            str(item.num or "").zfill(3),
            mult_key(item.mult or ""),
            Article._ORDER_POS[item.pos or ""],
        )

    articles = sorted(context.models(), key=_sort_key)
    return {"lecture": context.lecture_resource.model(), "articles": articles}


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
