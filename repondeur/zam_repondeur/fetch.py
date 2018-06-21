from pathlib import Path
from typing import List

from pyramid.threadlocal import get_current_registry
from tlfp.tools.parse_texte import parse

from zam_aspirateur.amendements.models import Amendement
from zam_aspirateur.__main__ import aspire_an, aspire_senat

from zam_repondeur.models import DBSession, Amendement as AmendementModel


def get_amendements(chambre: str, session: str, texte: int) -> List[Amendement]:
    title: str
    amendements: List[Amendement]
    if chambre == "senat":
        title, amendements = aspire_senat(session=session, num=texte)
        return amendements
    elif chambre == "an":
        settings = get_current_registry().settings
        title, amendements = aspire_an(
            legislature=int(session),
            texte=texte,
            groups_folder=Path(settings["zam.an_groups_folder"]),
        )
        return amendements
    else:
        raise NotImplementedError


def get_articles(chambre: str, session: str, texte: int) -> None:
    if chambre == "an":
        BASE_URL = "http://www.assemblee-nationale.fr/"
        is_commission = False  # TODO: keep from dossier/texte.
        if is_commission:
            url = f"{BASE_URL}{session}/ta-commission/r{texte:04}-a0.asp"
        else:
            url = f"{BASE_URL}{session}/projets/pl{texte:04}.asp"
    else:
        url = "http://www.senat.fr/leg/pjl17-063.html"
    items = parse(url)
    for article_content in items:
        if "alineas" in article_content and article_content["alineas"]:
            article_num = article_content["titre"].replace(" ", "-").replace("1er", "1")
            titre = [
                item["titre"]
                for item in items
                if article_content.get("section", False) == item.get("id")
            ][0] or ""
            DBSession.query(AmendementModel).filter(
                AmendementModel.chambre == chambre,
                AmendementModel.session == session,
                AmendementModel.num_texte == texte,
                AmendementModel.subdiv_num == article_num,
            ).update(
                {"subdiv_titre": titre, "subdiv_contenu": article_content["alineas"]}
            )
