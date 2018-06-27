from pathlib import Path
from typing import List, Tuple

from pyramid.threadlocal import get_current_registry
from tlfp.tools.parse_texte import parse

from zam_aspirateur.amendements.models import Amendement
from zam_aspirateur.__main__ import aspire_an, aspire_senat

from zam_repondeur.models import DBSession, Amendement as AmendementModel, Lecture


def get_amendements(
    chambre: str, session: str, texte: int
) -> Tuple[List[Amendement], List[str]]:
    title: str
    amendements: List[Amendement]
    if chambre == "senat":
        title, amendements = aspire_senat(session=session, num=texte)
        return amendements, []
    elif chambre == "an":
        settings = get_current_registry().settings
        title, amendements, errored = aspire_an(
            legislature=int(session),
            texte=texte,
            groups_folder=Path(settings["zam.an_groups_folder"]),
        )
        return amendements, errored
    else:
        raise NotImplementedError


def get_articles(lecture: Lecture) -> None:
    if lecture.chambre == "an":
        BASE_URL = "http://www.assemblee-nationale.fr/"
        if "Commission" in lecture.titre or "Séance" in lecture.titre:
            url = f"{BASE_URL}{lecture.session}/ta-commission/r{lecture.num_texte:04}-a0.asp"  # noqa
        else:
            url = f"{BASE_URL}{lecture.session}/projets/pl{lecture.num_texte:04}.asp"
    else:
        BASE_URL = "https://www.senat.fr/"
        url = f"{BASE_URL}leg/pjl{lecture.session[2:4]}-{lecture.num_texte:03}.html"
    items = parse(url)
    for article_content in items:
        if "alineas" in article_content and article_content["alineas"]:
            titre = article_content["titre"].replace("1er", "1")
            if " " in titre:
                article_num, article_mult = titre.split(" ", 1)
            else:
                article_num, article_mult = titre, ""
            section_titles = [
                item["titre"]
                for item in items
                if article_content.get("section", False) == item.get("id")
            ]
            section_title = section_titles and section_titles[0] or ""
            DBSession.query(AmendementModel).filter(
                AmendementModel.chambre == lecture.chambre,
                AmendementModel.session == lecture.session,
                AmendementModel.num_texte == lecture.num_texte,
                AmendementModel.subdiv_num == article_num,
                AmendementModel.subdiv_mult == article_mult,
            ).update(
                {
                    "subdiv_titre": section_title,
                    "subdiv_contenu": article_content["alineas"],
                }
            )
