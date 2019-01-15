from difflib import Differ
from typing import List, Optional, Dict, Callable, Any

from jinja2 import Markup, contextfilter
from jinja2.filters import do_striptags
from jinja2.runtime import Context

from zam_repondeur.models import Article, Lecture


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
        if amendement.is_displayable
    }
    return matches


def filter_out_empty_additionals(all_articles: List[Article]) -> List[Article]:
    articles = []
    for article in all_articles:
        if article.pos:
            for amendement in article.amendements:
                if amendement.is_displayable:
                    articles.append(article)
                    break
        else:
            articles.append(article)
    return articles


def render_diff(old: str, new: str) -> str:
    differ = Differ()
    results = differ.compare([old], [new])
    # https://docs.python.org/3/library/difflib.html#difflib.Differ
    mapper: Dict[str, Callable[[Any], Any]] = {
        "-": lambda x: f"<del>« {do_striptags(x)} »</del> à ",  # type: ignore
        "+": lambda x: f"<ins>« {do_striptags(x)} »</ins>",  # type: ignore
        "": lambda x: x,
        "?": lambda x: x,  # Not sure what to display in that case.
    }
    content = ""
    for result in results:
        code, text = result.split(" ", 1)
        content += mapper[code](text)
    return Markup(content)
