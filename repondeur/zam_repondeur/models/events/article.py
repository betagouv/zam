from string import Template
from typing import Any, Optional

from jinja2 import Markup
from lxml.html.diff import htmldiff  # nosec
from pyramid.request import Request

from ..article import Article
from ..chambre import Chambre
from .base import Event


class ArticleEvent(Event):
    def __init__(
        self, article: Article, request: Optional[Request] = None, **kwargs: Any
    ):
        super().__init__(request=request, **kwargs)
        self.article = article

    @property
    def template_vars(self) -> dict:
        template_vars = {
            "new_value": self.data["new_value"],
            "old_value": self.data["old_value"],
        }
        if self.user:
            template_vars.update({"user": self.user.name, "email": self.user.email})
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
        chambre = self.article.lecture.chambre
        if chambre == Chambre.AN:
            de_qui = "de l’Asssemblée nationale"
        elif chambre == Chambre.SENAT:
            de_qui = "du Sénat"
        else:
            raise ValueError(f"Unsupported chambre {chambre}")
        return Template(
            f"Le contenu de l’article a été modifié par les services {de_qui}."
        )

    def __init__(self, article: Article, content: dict) -> None:
        super().__init__(
            article=article, old_value=article.content or {}, new_value=content
        )

    def apply(self) -> None:
        self.article.content = self.data["new_value"]

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
            return Template(f"<abbr title='$email'>$user</abbr> a {action} le titre.")
        chambre = self.article.lecture.chambre
        if chambre == Chambre.AN:
            de_qui = "de l’Asssemblée nationale"
        elif chambre == Chambre.SENAT:
            de_qui = "du Sénat"
        else:
            raise ValueError(f"Unsupported chambre {chambre}")
        return Template(
            f"Le titre de l’article a été modifié par les services {de_qui}."
        )

    def __init__(
        self, article: Article, title: str, request: Optional[Request] = None
    ) -> None:
        super().__init__(
            article=article,
            old_value=article.user_content.title,
            new_value=title,
            request=request,
        )

    def apply(self) -> None:
        self.article.user_content.title = self.data["new_value"]


class PresentationArticleModifiee(ArticleEvent):
    __mapper_args__ = {"polymorphic_identity": "presentation_article_modifiee"}

    icon = "edit"

    @property
    def summary_template(self) -> Template:
        action = "modifié" if self.template_vars["old_value"] else "ajouté"
        return Template(
            f"<abbr title='$email'>$user</abbr> a {action} la présentation."
        )

    def __init__(self, article: Article, presentation: str, request: Request) -> None:
        super().__init__(
            article=article,
            old_value=article.user_content.presentation,
            new_value=presentation,
            request=request,
        )

    def apply(self) -> None:
        self.article.user_content.presentation = self.data["new_value"]
