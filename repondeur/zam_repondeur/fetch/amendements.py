from typing import List, Tuple

from zam_repondeur.fetch.an.amendements import aspire_an
from zam_repondeur.fetch.senat.amendements import aspire_senat
from zam_repondeur.models import Amendement, Lecture


def get_amendements(lecture: Lecture) -> Tuple[List[Amendement], int, List[str]]:
    title: str
    if lecture.chambre == "senat":
        amendements, created = aspire_senat(lecture=lecture)
        return amendements, created, []  # Not pertinent in that case (unique file).
    elif lecture.chambre == "an":
        amendements, created, errored = aspire_an(lecture=lecture)
        return amendements, created, errored
    else:
        raise NotImplementedError
