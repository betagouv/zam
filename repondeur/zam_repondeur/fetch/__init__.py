import logging
from functools import partial
from typing import Any, Callable, Dict, List, Tuple

from tlfp.tools.parse_texte import parse

from zam_repondeur.fetch.an.amendements import aspire_an
from zam_repondeur.fetch.exceptions import NotFound
from zam_repondeur.models import Amendement
from zam_repondeur.fetch.senat.amendements import aspire_senat
from zam_repondeur.models import DBSession, Article, Lecture, get_one_or_create

logger = logging.getLogger(__name__)


def get_amendements(lecture: Lecture) -> Tuple[List[Amendement], int, List[str]]:
    title: str
    amendements: List[Amendement]
    if lecture.chambre == "senat":
        amendements, created = aspire_senat(lecture=lecture)
        return amendements, created, []  # Not pertinent in that case (unique file).
    elif lecture.chambre == "an":
        amendements, created, errored = aspire_an(lecture=lecture)
        return amendements, created, errored
    else:
        raise NotImplementedError


def get_section_title(items: List[Dict[str, Any]], article: dict) -> str:
    for item in items:
        if article.get("section", False) == item.get("id"):
            title: str = item["titre"]
            return title
    return ""


def get_article_num_mult(title: str) -> Tuple[str, str]:
    title = title.replace("1er", "1").replace("liminaire", "0")
    if " " in title:
        num, mult = title.split(" ", 1)
        return num, mult
    else:
        return title, ""


def get_article_nums_mults(article: Dict[str, Any]) -> List[Tuple[str, str]]:
    title = article["titre"]
    if " à " in title:
        start, end = title.split(" à ")
        # We are not handling `5 bis à 8 ter AAA` (yet?).
        return [(str(num), "") for num in range(int(start), int(end) + 1)]
    else:
        return [get_article_num_mult(title)]


def get_articles(lecture: Lecture) -> bool:
    urls = get_possible_texte_urls(lecture)
    try:
        articles = parse_first_working_url(urls)
    except NotFound:
        logger.warning("Texte non trouvé : %r (%s)", lecture, urls)
        return False
    return update_lecture_articles(lecture, articles)


AN_URL = "http://www.assemblee-nationale.fr/"
SENAT_URL = "https://www.senat.fr/"


def get_possible_texte_urls(lecture: Lecture) -> List[str]:
    if lecture.chambre == "an":
        return [
            f"{AN_URL}{lecture.session}/projets/pl{lecture.num_texte:04}.asp",
            f"{AN_URL}{lecture.session}/ta-commission/r{lecture.num_texte:04}-a0.asp",
        ]
    else:
        return [f"{SENAT_URL}leg/pjl{lecture.session[2:4]}-{lecture.num_texte:03}.html"]


def parse_first_working_url(urls: List[str]) -> List[dict]:
    for url in urls:
        articles: List[dict] = parse(url)
        if len(articles) > 1:
            return articles
    raise NotFound


def update_lecture_articles(lecture: Lecture, all_article_data: List[dict]) -> bool:
    changed = False
    for article_data in all_article_data:
        if article_data["type"] in {"texte", "section"}:
            continue
        articles = find_or_create_articles(lecture, article_data)
        for article in articles:
            changed |= update_article_contents(article, article_data)
            changed |= set_default_article_title(
                article, article_data, partial(get_section_title, all_article_data)
            )
    return changed


def find_or_create_articles(lecture: Lecture, article_data: dict) -> List[Article]:
    nums_mults = get_article_nums_mults(article_data)
    return [
        get_one_or_create(
            DBSession,
            Article,
            lecture=lecture,
            type=article_data["type"],
            num=num,
            mult=mult,
            pos="",
        )[0]
        for num, mult in nums_mults
    ]


def update_article_contents(article: Article, article_data: dict) -> bool:
    contenu = article_data.get("alineas")
    if contenu is not None and contenu != article.contenu:
        article.contenu = contenu
        return True
    return False


def set_default_article_title(
    article: Article, article_data: dict, get_default_title: Callable
) -> bool:
    """
    If the article does not have a title, we set it to the parent section title
    """
    if not article.titre:
        default_title = get_default_title(article_data)
        if default_title:
            article.titre = default_title
            return True
    return False
