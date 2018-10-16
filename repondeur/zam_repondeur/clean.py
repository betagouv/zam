from html import unescape
from typing import Iterable, Optional

import bleach


ALLOWED_TAGS = [
    "div",
    "p",
    "h3",
    "ul",
    "ol",
    "li",
    "b",
    "i",
    "strong",
    "em",
    "sub",
    "sup",
]
TABLE_TAGS = ["table", "thead", "th", "tbody", "tr", "td"]


def clean_html(html: str, allowed_tags: Optional[Iterable[str]] = None) -> str:
    if allowed_tags is None:
        allowed_tags = ALLOWED_TAGS + TABLE_TAGS
    text = unescape(html)  # decode HTML entities
    sanitized: str = bleach.clean(text, tags=allowed_tags, strip=True)
    return sanitized.strip()
