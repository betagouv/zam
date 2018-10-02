import logging
from typing import Sequence

from zam_repondeur.models import Amendement, Lecture


logger = logging.getLogger(__name__)


def clear_position_if_removed(
    lecture: Lecture, amendements: Sequence[Amendement]
) -> None:
    removed_from_discussion = set(lecture.amendements) - set(amendements)
    for amendement in removed_from_discussion:
        logger.info("Amendement %s retiré de la discussion", amendement.num)
        amendement.position = None
