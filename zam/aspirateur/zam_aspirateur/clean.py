from html import unescape

import bleach


def clean_html(text: str) -> str:
    return bleach.clean(unescape(text), tags=['p', 'sup']).strip()
