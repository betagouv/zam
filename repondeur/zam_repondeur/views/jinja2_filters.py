from typing import Optional

from jinja2 import Markup


def paragriphy(content: Optional[str]) -> Markup:
    if content is None:
        content = ""
    if not content.startswith("<p>"):
        content = f"<p>{content}</p>"
    return Markup(content)
