from pathlib import Path
from typing import List, Tuple

from zam_aspirateur.amendements.fetch_an import fetch_and_parse_all, NotFound
from zam_aspirateur.amendements.models import Amendement


def aspire_an(
    legislature: int, texte: int, organe: str, groups_folder: Path
) -> Tuple[str, List[Amendement], List[str]]:
    print("Récupération du titre et des amendements déposés...")
    try:
        title, amendements, errored = fetch_and_parse_all(
            legislature=legislature,
            texte=texte,
            organe=organe,
            groups_folder=groups_folder,
        )
    except NotFound:
        return "", [], []

    return title, amendements, errored
