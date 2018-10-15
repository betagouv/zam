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
            titre: str = item["titre"]
            return titre
    return ""


def get_article_num_mult(article: Dict[str, Any]) -> Tuple[str, str]:
    titre = article["titre"].replace("1er", "1").replace("liminaire", "0")
    if " " in titre:
        num, mult = titre.split(" ", 1)
        return num, mult
    else:
        return titre, ""


def get_articles(lecture: Lecture) -> None:
    urls = get_possible_texte_urls(lecture)
    try:
        articles = parse_first_working_url(urls)
    except NotFound:
        logger.warning("Texte non trouvé : %r (%s)", lecture, urls)
        return
    update_lecture_articles(lecture, articles)


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


def update_lecture_articles(lecture: Lecture, all_article_data: List[dict]) -> None:
    for article_data in all_article_data:
        if article_data["type"] in {"texte", "section"}:
            continue
        article = find_or_create_article(lecture, article_data)
        update_article_contents(article, article_data)
        set_default_article_title(
            article, article_data, partial(get_section_title, all_article_data)
        )


def find_or_create_article(lecture: Lecture, article_data: dict) -> Article:
    num, mult = get_article_num_mult(article_data)
    article: Article
    article, _ = get_one_or_create(
        DBSession,
        Article,
        lecture=lecture,
        type=article_data["type"],
        num=num,
        mult=mult,
        pos="",
    )
    return article


def update_article_contents(article: Article, article_data: dict) -> None:
    contenu = article_data.get("alineas")
    if contenu is not None:
        article.contenu = contenu


def set_default_article_title(
    article: Article, article_data: dict, get_default_title: Callable
) -> None:
    """
    If the article does not have a title, we set it to the parent section title
    """
    if not article.titre:
        article.titre = get_default_title(article_data)
