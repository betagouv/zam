from html import unescape

from bleach import Cleaner


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
    "table",
    "thead",
    "th",
    "tbody",
    "tr",
    "td",
]


CLEANER = Cleaner(tags=ALLOWED_TAGS, strip=True)


def clean_html(html: str) -> str:
    text = unescape(html)  # decode HTML entities
    sanitized: str = CLEANER.clean(text)
    return sanitized.strip()
