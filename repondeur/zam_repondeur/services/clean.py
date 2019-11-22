import threading
from html import unescape

from bleach.sanitizer import Cleaner

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

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
    "abbr": ["title"],
    "acronym": ["title"],
    "td": ["colspan"],
    "th": ["colspan"],
}


# Bleach uses html5lib, which is not thread-safe, so we have to use a cleaner instance
# per thread instead of a global one to avoid transient errors in our workers
#
# See: https://github.com/mozilla/bleach/issues/370
#
_THREAD_LOCALS = threading.local()


def clean_html(html: str) -> str:
    text = unescape(html)  # decode HTML entities

    if not hasattr(_THREAD_LOCALS, "cleaner"):
        _THREAD_LOCALS.cleaner = Cleaner(
            tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True
        )

    sanitized: str = _THREAD_LOCALS.cleaner.clean(text)
    return sanitized.strip()


def clean_all_html(html: str) -> str:
    text = unescape(html)  # decode HTML entities

    if not hasattr(_THREAD_LOCALS, "cleaner_all"):
        _THREAD_LOCALS.cleaner_all = Cleaner(tags=[], attributes={}, strip=True)

    sanitized: str = _THREAD_LOCALS.cleaner_all.clean(text)
    return sanitized.strip()
