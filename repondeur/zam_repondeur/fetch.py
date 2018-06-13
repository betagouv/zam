from typing import List

from zam_aspirateur.amendements.models import Amendement
from zam_aspirateur.amendements.fetch_senat import fetch_and_parse_all, NotFound
from zam_aspirateur.__main__ import process_amendements


def get_amendements_senat(session: str, num_texte: str) -> List[Amendement]:
    amendements = fetch_and_parse_all(session=session, num=num_texte)
    processed_amendements: List[Amendement] = process_amendements(
        amendements=amendements, session=session, num=num_texte
    )
    return processed_amendements


__all__ = ["get_amendements_senat", "NotFound"]
