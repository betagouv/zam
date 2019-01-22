from typing import Any
from string import Template

from jinja2 import Markup
from jinja2.filters import do_striptags
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

    details_template = Template(
        "De <del>« $old_value »</del> à <ins>« $new_value »</ins>"
    )

    def __init__(self, request: Request, article: Article, **kwargs: Any):
        super().__init__(request, **kwargs)
        self.article = article

    @property
    def template_vars(self) -> dict:
        template_vars = {
            "new_value": do_striptags(self.data["new_value"]),  # type: ignore
            "old_value": do_striptags(self.data["old_value"]),  # type: ignore
        }
        if self.user:
            template_vars.update(
                {"user": self.user.display_name, "email": self.user.email}
            )
        return template_vars

    def render_summary(self) -> str:
        return Markup(self.summary_template.safe_substitute(**self.template_vars))

    def render_details(self) -> str:
        return Markup(self.details_template.safe_substitute(**self.template_vars))


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

    details_template = Template("")

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


class TitreArticleModifie(ArticleEvent):
    __mapper_args__ = {"polymorphic_identity": "titre_article_modifie"}

    @property
    def summary_template(self) -> Template:
        if self.user:
            return Template("<abbr title='$email'>$user</abbr> a modifié le titre")
        if self.article.lecture.chambre == "an":
            de_qui = "de l’Asssemblée nationale"
        else:
            de_qui = "du Sénat"
        return Template(
            f"Le titre de l’article a été modifié par les services {de_qui}"
        )

    @property
    def icon(self) -> str:
        return "edit" if self.user else "document"

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


class PresentationArticleModifiee(ArticleEvent):
    __mapper_args__ = {"polymorphic_identity": "presentation_article_modifiee"}

    summary_template = Template(
        "<abbr title='$email'>$user</abbr> a modifié la présentation"
    )
    icon = "edit"

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
