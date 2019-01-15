from typing import Any

from pyramid.threadlocal import get_current_request
from sqlalchemy import event
from sqlalchemy.util import symbol

from ..models import ArticleUserContent, ArticleUserContentRevision, DBSession


@event.listens_for(ArticleUserContent.title, "set", active_history=True)
@event.listens_for(ArticleUserContent.presentation, "set", active_history=True)
def article_user_content_updated(
    target: ArticleUserContent, value: str, old_value: str, initiator: Any
) -> None:
    request = get_current_request()
    user = request.user if request else None
    if value != old_value and old_value != symbol("NEVER_SET"):
        revision = ArticleUserContentRevision(
            user=user,
            user_content=target,
            article=target.article,
            title=target.title,
            presentation=target.presentation,
        )
        DBSession.add(revision)
