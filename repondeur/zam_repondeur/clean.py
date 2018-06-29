import bleach


ALLOWED_TAGS = ["p", "ul", "li", "b", "i", "strong", "em"]


def clean_html(text: str) -> str:
    cleaned: str = bleach.clean(text, strip=True, tags=ALLOWED_TAGS)
    return cleaned
