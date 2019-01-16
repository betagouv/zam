from typing import Any
from string import Template

from jinja2 import Markup
from jinja2.filters import do_striptags
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
                old_value=do_striptags(self.data["old_value"]),
                new_value=do_striptags(self.data["new_value"]),
            )
        )


class UpdateArticlePresentation(ArticleEvent):
    """
    A user updated an article's presentation
    """

    __mapper_args__ = {"polymorphic_identity": "update_article_presentation"}

    summary_template = Template(
        "<abbr title='$email'>$user</abbr> a modifié la présentation"
    )

    def __init__(self, article: Article, presentation: str) -> None:
        super().__init__(
            article, old_value=article.user_content.presentation, new_value=presentation
        )

    def apply(self) -> None:
        self.article.user_content.presentation = self.data["new_value"]


class UpdateArticleTitle(ArticleEvent):
    """
    A user updated an article's title
    """

    __mapper_args__ = {"polymorphic_identity": "update_article_title"}

    summary_template = Template("<abbr title='$email'>$user</abbr> a modifié le titre")

    def __init__(self, article: Article, title: str) -> None:
        super().__init__(article, old_value=article.user_content.title, new_value=title)

    def apply(self) -> None:
        self.article.user_content.title = self.data["new_value"]
