from typing import Union

from jinja2 import Markup


def paragriphy(content: Markup) -> Union[Markup, str]:
    if not content.startswith("<p>"):
        content = Markup(f"<p>{content}</p>")
    return content
