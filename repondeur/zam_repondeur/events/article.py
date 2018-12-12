from typing import Any

from sqlalchemy import event

from ..models import Article, ArticleRevision, DBSession


@event.listens_for(Article.mult, "set", active_history=True)
def mult_updated(target: Article, value: str, old_value: str, initiator: Any) -> None:
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
