from typing import Any, Dict, List, Tuple

from tlfp.tools.parse_texte import parse

from zam_repondeur.fetch.an.amendements import aspire_an
from zam_repondeur.fetch.exceptions import NotFound
from zam_repondeur.models import Amendement
from zam_repondeur.fetch.senat.amendements import aspire_senat
from zam_repondeur.models import DBSession, Article, Lecture


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
    titre = article["titre"].replace("1er", "1")
    if " " in titre:
        num, mult = titre.split(" ", 1)
        return num, mult
    else:
        return titre, ""


def get_articles(lecture: Lecture) -> None:
    urls = get_possible_texte_urls(lecture)
    articles = parse_first_working_url(urls)
    add_article_contents_to_amendements(lecture, articles)


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


def add_article_contents_to_amendements(lecture: Lecture, articles: List[dict]) -> None:
    for article_content in articles:
        if "alineas" in article_content and article_content["alineas"]:
            article_num, article_mult = get_article_num_mult(article_content)
            section_title = get_section_title(articles, article_content)
            DBSession.query(Article).filter_by(
                lecture=lecture, num=article_num, mult=article_mult
            ).update({"titre": section_title, "contenu": article_content["alineas"]})
