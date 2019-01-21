from typing import Any
from string import Template

from jinja2 import Markup
from jinja2.filters import do_striptags
from pyramid.request import Request
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import backref, relationship

from .base import Event
from ..models.article import Article


class ArticleEvent(Event):
    article_pk = Column(Integer, ForeignKey("articles.pk"))
    article = relationship(
        Article, backref=backref("events", order_by=Event.created_at.desc())
    )

    details_template = Template(
        "De <del>« $old_value »</del> à <ins>« $new_value »</ins>"
    )

    def __init__(self, article: Article, **kwargs: Any):
        super().__init__(**kwargs)
        self.article = article

    def render_summary(self) -> str:
        return Markup(
            self.summary_template.safe_substitute(
                user=self.user.display_name, email=self.user.email
            )
        )

    def render_details(self) -> str:
        return Markup(
            self.details_template.safe_substitute(
                old_value=do_striptags(self.data["old_value"]),  # type: ignore
                new_value=do_striptags(self.data["new_value"]),  # type: ignore
            )
        )


class TitreArticleModifie(ArticleEvent):
    __mapper_args__ = {"polymorphic_identity": "titre_article_modifie"}

    summary_template = Template("<abbr title='$email'>$user</abbr> a modifié le titre")

    def __init__(
        self, request: Request, article: Article, title: str, **kwargs: Any
    ) -> None:
        super().__init__(
            request=request,
            article=article,
            old_value=article.user_content.title,
            new_value=title,
            **kwargs
        )

    def apply(self) -> None:
        self.article.user_content.title = self.data["new_value"]


class PresentationArticleModifiee(ArticleEvent):
    __mapper_args__ = {"polymorphic_identity": "presentation_article_modifiee"}

    summary_template = Template(
        "<abbr title='$email'>$user</abbr> a modifié la présentation"
    )

    def __init__(
        self, request: Request, article: Article, presentation: str, **kwargs: Any
    ) -> None:
        super().__init__(
            request=request,
            article=article,
            old_value=article.user_content.presentation,
            new_value=presentation,
            **kwargs
        )

    def apply(self) -> None:
        self.article.user_content.presentation = self.data["new_value"]
