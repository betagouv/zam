from datetime import datetime
from typing import Any
from string import Template

from jinja2 import Markup
from lxml.html.diff import htmldiff
from pyramid.request import Request
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import backref, relationship

from .base import Event
from ..article import Article


class ArticleEvent(Event):
    article_pk = Column(Integer, ForeignKey("articles.pk"))
    article = relationship(
        Article, backref=backref("events", order_by=Event.created_at.desc())
    )

    def __init__(self, request: Request, article: Article, **kwargs: Any):
        super().__init__(request, **kwargs)
        self.article = article

    @property
    def template_vars(self) -> dict:
        template_vars = {
            "new_value": self.data["new_value"],
            "old_value": self.data["old_value"],
        }
        if self.user:
            template_vars.update(
                {"user": self.user.display_name, "email": self.user.email}
            )
        return template_vars

    def render_summary(self) -> str:
        return Markup(self.summary_template.safe_substitute(**self.template_vars))

    def render_details(self) -> str:
        return Markup(
            htmldiff(self.template_vars["old_value"], self.template_vars["new_value"])
        )


class ContenuArticleModifie(ArticleEvent):
    __mapper_args__ = {"polymorphic_identity": "contenu_article_modifie"}

    icon = "document"

    @property
    def summary_template(self) -> Template:
        if self.article.lecture.chambre == "an":
            de_qui = "de l’Asssemblée nationale"
        else:
            de_qui = "du Sénat"
        return Template(
            f"Le contenu de l’article a été modifié par les services {de_qui}"
        )

    def __init__(
        self, request: Request, article: Article, content: dict, **kwargs: Any
    ) -> None:
        super().__init__(
            request,
            article,
            old_value=article.content or {},
            new_value=content,
            **kwargs,
        )

    def apply(self) -> None:
        self.article.content = self.data["new_value"]
        self.article.modified_at = datetime.utcnow()

    def render_details(self) -> str:
        return ""


class TitreArticleModifie(ArticleEvent):
    __mapper_args__ = {"polymorphic_identity": "titre_article_modifie"}

    @property
    def icon(self) -> str:
        return "edit" if self.user else "document"

    @property
    def summary_template(self) -> Template:
        if self.user:
            action = "modifié" if self.template_vars["old_value"] else "ajouté"
            return Template(f"<abbr title='$email'>$user</abbr> a {action} le titre")
        if self.article.lecture.chambre == "an":
            de_qui = "de l’Asssemblée nationale"
        else:
            de_qui = "du Sénat"
        return Template(
            f"Le titre de l’article a été modifié par les services {de_qui}"
        )

    def __init__(
        self, request: Request, article: Article, title: str, **kwargs: Any
    ) -> None:
        super().__init__(
            request=request,
            article=article,
            old_value=article.user_content.title,
            new_value=title,
            **kwargs,
        )

    def apply(self) -> None:
        self.article.user_content.title = self.data["new_value"]
        self.article.modified_at = datetime.utcnow()


class PresentationArticleModifiee(ArticleEvent):
    __mapper_args__ = {"polymorphic_identity": "presentation_article_modifiee"}

    icon = "edit"

    @property
    def summary_template(self) -> Template:
        action = "modifié" if self.template_vars["old_value"] else "ajouté"
        return Template(f"<abbr title='$email'>$user</abbr> a {action} la présentation")

    def __init__(
        self, request: Request, article: Article, presentation: str, **kwargs: Any
    ) -> None:
        super().__init__(
            request=request,
            article=article,
            old_value=article.user_content.presentation,
            new_value=presentation,
            **kwargs,
        )

    def apply(self) -> None:
        self.article.user_content.presentation = self.data["new_value"]
        self.article.modified_at = datetime.utcnow()
