import logging
from http import HTTPStatus
from typing import Any, Dict, Iterable, Iterator, List, NamedTuple, Optional, Tuple

import requests

from zam_repondeur.models import Amendement, Lecture
from ..missions import MISSIONS, Mission


BASE_URL = "https://www.senat.fr"


logger = logging.getLogger(__name__)


class DiscussionDetails(NamedTuple):
    num: int
    position: int
    id_discussion_commune: Optional[int]
    id_identique: Optional[int]
    parent_num: Optional[int]
    mission: Optional[Mission]


def fetch_and_parse_discussion_details(lecture: Lecture) -> List[DiscussionDetails]:
    data_iter = _fetch_discussion_details(lecture)
    return _parse_derouleur_data(data_iter)


def _fetch_discussion_details(lecture: Lecture) -> Iterator[Tuple[Any, Mission]]:
    """
    Récupère les amendements à discuter, dans l'ordre de passage

    NB : les amendements jugés irrecevables ne sont pas inclus.
    """
    for url, mission in derouleur_urls_and_missions(lecture):
        resp = requests.get(url)
        if resp.status_code == HTTPStatus.NOT_FOUND:  # 404
            logger.warning(f"Could not fetch {url}")
            continue
        if resp.text == "":
            logger.warning(f"Empty response for {url}")
            continue
        yield resp.json(), mission


def _parse_derouleur_data(
    data_iter: Iterable[Tuple[Any, Mission]]
) -> List[DiscussionDetails]:
    subdivs_amends_missions = [
        (subdiv, amend, mission)
        for data, mission in data_iter
        for subdiv in data["Subdivisions"]
        for amend in subdiv["Amendements"]
    ]

    uid_map: Dict[str, int] = {
        amend["idAmendement"]: Amendement.parse_num(amend["num"])[0]
        for _, amend, _ in subdivs_amends_missions
    }

    discussion_details = [
        parse_discussion_details(uid_map, amend, position, mission)
        for position, (subdiv, amend, mission) in enumerate(
            subdivs_amends_missions, start=1
        )
    ]

    return discussion_details


def derouleur_urls_and_missions(lecture: Lecture) -> Iterator[Tuple[str, Mission]]:
    assert lecture.texte.session_str is not None  # nosec (mypy hint)
    missions = (
        MISSIONS.get(lecture.texte.session_str, {})
        .get(lecture.texte.numero, {})
        .get(lecture.partie)
    )
    phase = "commission" if lecture.is_commission else "seance"
    if missions is not None:
        for mission in missions:
            yield (
                f"{BASE_URL}/en{phase}/{lecture.texte.session_str}"
                f"/{lecture.texte.numero}/liste_discussion_{mission.num}.json",
                mission,
            )
    else:
        yield (
            f"{BASE_URL}/en{phase}/{lecture.texte.session_str}"
            f"/{lecture.texte.numero}/liste_discussion.json",
            Mission(num=None, titre="", titre_court=""),
        )


def parse_discussion_details(
    uid_map: Dict[str, int], amend: dict, position: int, mission: Mission
) -> DiscussionDetails:
    num, rectif = Amendement.parse_num(amend["num"])
    details = DiscussionDetails(
        num=num,
        position=position,
        id_discussion_commune=(
            int(amend["idDiscussionCommune"])
            if parse_bool(amend["isDiscussionCommune"])
            else None
        ),
        id_identique=(
            int(amend["idIdentique"]) if parse_bool(amend["isIdentique"]) else None
        ),
        parent_num=get_parent_num(uid_map, amend),
        mission=mission if mission.titre else None,
    )
    return details


def parse_bool(text: str) -> bool:
    if text == "true":
        return True
    if text == "false":
        return False
    raise ValueError


def get_parent_num(uid_map: Dict[str, int], amend: dict) -> Optional[int]:
    if (
        "isSousAmendement" in amend
        and parse_bool(amend["isSousAmendement"])
        and "idAmendementPere" in amend
    ):
        parent_uid = amend["idAmendementPere"]
        if parent_uid in uid_map:
            return uid_map[parent_uid]
        else:
            logger.warning("Unknown parent amendement %s", parent_uid)
    return None
