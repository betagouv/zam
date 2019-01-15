from typing import Any

# from pyramid.threadlocal import get_current_request
from sqlalchemy import Column, ForeignKey, Integer

# from sqlalchemy import event
from sqlalchemy.orm import backref, relationship

# from sqlalchemy.util import symbol

from .base import Event
from ..models.article import Article

# from ..models import (
#     # ArticleUserContent,
#     # ArticleUserContentRevision,
#     # DBSession
# )


# @event.listens_for(ArticleUserContent.title, "set", active_history=True)
# @event.listens_for(ArticleUserContent.presentation, "set", active_history=True)
# def article_user_content_updated(
#     target: ArticleUserContent, value: str, old_value: str, initiator: Any
# ) -> None:
#     request = get_current_request()
#     user = request.user if request else None
#     if value != old_value and old_value != symbol("NEVER_SET"):
#         revision = ArticleUserContentRevision(
#             user=user,
#             user_content=target,
#             article=target.article,
#             title=target.title,
#             presentation=target.presentation,
#         )
#         DBSession.add(revision)


class ArticleEvent(Event):
    article_pk = Column(Integer, ForeignKey("articles.pk"))
    article = relationship(Article, backref=backref("events", order_by=Event.created_at.desc()))

    def __init__(self, article: Article, **kwargs: Any):
        super().__init__(**kwargs)
        self.article = article


class UpdateArticlePresentation(ArticleEvent):
    """
    A user updated an article's presentation
    """

    __mapper_args__ = {"polymorphic_identity": "update_article_presentation"}

    action = "a modifié la présentation de"

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

    action = "a modifié le titre de"

    def __init__(self, article: Article, title: str) -> None:
        super().__init__(article, old_value=article.user_content.title, new_value=title)

    def apply(self) -> None:
        self.article.user_content.title = self.data["new_value"]
