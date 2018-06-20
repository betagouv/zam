from pathlib import Path
from typing import List

from pyramid.threadlocal import get_current_registry

from zam_aspirateur.amendements.models import Amendement
from zam_aspirateur.__main__ import aspire_an, aspire_senat


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
