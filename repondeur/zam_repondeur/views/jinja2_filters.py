from jinja2 import Markup


def paragriphy(content: str) -> Markup:
    if not content.startswith("<p>"):
        content = f"<p>{content}</p>"
    return Markup(content)
