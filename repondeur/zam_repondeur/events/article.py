from typing import Any

from sqlalchemy import event
from sqlalchemy.util import symbol

from ..models import ArticleUserContent, ArticleUserContentRevision, DBSession


@event.listens_for(ArticleUserContent.title, "set", active_history=True)
@event.listens_for(ArticleUserContent.presentation, "set", active_history=True)
def article_user_content_updated(
    target: ArticleUserContent, value: str, old_value: str, initiator: Any
) -> None:
    current_request = DBSession.registry.scopefunc()
    user = current_request and current_request.user or None
    if value != old_value and old_value != symbol("NEVER_SET"):
        revision = ArticleUserContentRevision(
            user=user,
            user_content=target,
            article=target.article,
            title=target.title,
            presentation=target.presentation,
        )
        DBSession.add(revision)
