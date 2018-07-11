from pathlib import Path
from typing import Any, Dict, List, Tuple

from pyramid.threadlocal import get_current_registry
from tlfp.tools.parse_texte import parse

from zam_aspirateur.amendements.models import Amendement
from zam_aspirateur.exceptions import NotFound

from zam_repondeur.fetch.an.amendements import aspire_an
from zam_repondeur.fetch.senat.amendements import aspire_senat
from zam_repondeur.models import DBSession, Amendement as AmendementModel, Lecture


def get_amendements(
    chambre: str, session: str, texte: int, organe: str
) -> Tuple[List[Amendement], List[str]]:
    title: str
    amendements: List[Amendement]
    if chambre == "senat":
        title, amendements = aspire_senat(session=session, num=texte, organe=organe)
        return amendements, []
    elif chambre == "an":
        settings = get_current_registry().settings
        title, amendements, errored = aspire_an(
            legislature=int(session),
            texte=texte,
            organe=organe,
            groups_folder=Path(settings["zam.an_groups_folder"]),
        )
        return amendements, errored
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
        if articles:
            return articles
    raise NotFound


def add_article_contents_to_amendements(lecture: Lecture, articles: List[dict]) -> None:
    for article_content in articles:
        if "alineas" in article_content and article_content["alineas"]:
            article_num, article_mult = get_article_num_mult(article_content)
            section_title = get_section_title(articles, article_content)
            DBSession.query(AmendementModel).filter(
                AmendementModel.chambre == lecture.chambre,
                AmendementModel.session == lecture.session,
                AmendementModel.num_texte == lecture.num_texte,
                AmendementModel.organe == lecture.organe,
                AmendementModel.subdiv_num == article_num,
                AmendementModel.subdiv_mult == article_mult,
            ).update(
                {
                    "subdiv_titre": section_title,
                    "subdiv_contenu": article_content["alineas"],
                }
            )
