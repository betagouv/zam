from html import unescape

import bleach


ALLOWED_TAGS = [
    'b',
    'div',
    'p',
    'sup',
]


def clean_html(html: str) -> str:
    text = unescape(html)  # decode HTML entities
    sanitized = bleach.clean(text, tags=ALLOWED_TAGS, strip=True)
    return sanitized.strip()
