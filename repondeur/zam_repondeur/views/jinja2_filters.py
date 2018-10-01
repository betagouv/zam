from typing import Optional

from jinja2 import Markup, contextfilter
from jinja2.runtime import Context

from zam_repondeur.models import Lecture


def paragriphy(content: Optional[str]) -> Markup:
    if content is None:
        content = ""
    if not content.startswith("<p>"):
        content = f"<p>{content}</p>"
    return Markup(content)


@contextfilter
def amendement_matches(context: Context, lecture: Lecture) -> dict:
    resource_context = (
        context["context"].parent if "article" in context else context["context"]
    )
    matches = {
        amendement.num: context["request"].resource_url(
            resource_context,
            amendement.article.url_key,
            "reponses",
            anchor=amendement.slug,
        )
        for amendement in lecture.amendements
    }
    return matches
