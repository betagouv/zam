from typing import Any

from sqlalchemy import event
from sqlalchemy.util import symbol

from ..models import Article, ArticleRevision, DBSession


@event.listens_for(Article.mult, "set", active_history=True)
@event.listens_for(Article.pos, "set", active_history=True)
def article_updated(
    target: Article, value: str, old_value: str, initiator: Any
) -> None:
    if value != old_value and old_value != symbol("NEVER_SET"):
        revision = ArticleRevision(
            article=target,
            lecture=target.lecture,
            type=target.type,
            num=target.num,
            mult=target.mult,
            pos=target.pos,
            content=target.content,
        )
        DBSession.add(revision)
