from http import HTTPStatus
from typing import Any, Dict, List, NamedTuple, Optional

import requests

from zam_repondeur.fetch.exceptions import NotFound
from zam_repondeur.models import Amendement, Lecture


BASE_URL = "https://www.senat.fr"


class DiscussionDetails(NamedTuple):
    num: int
    position: int
    discussion_commune: Optional[int]
    identique: bool
    parent_num: Optional[int]


def fetch_and_parse_discussion_details(
    lecture: Lecture, phase: str
) -> List[DiscussionDetails]:
    try:
        data = _fetch_discussion_details(lecture, phase)
    except NotFound:
        return []
    subdivs_amends = [
        (subdiv, amend)
        for subdiv in data["Subdivisions"]
        for amend in subdiv["Amendements"]
    ]
    uid_map: Dict[str, int] = {}
    discussion_details = []
    for position, (subdiv, amend) in enumerate(subdivs_amends, start=1):
        details = parse_discussion_details(uid_map, amend, position)
        uid_map[amend["idAmendement"]] = details.num
        discussion_details.append(details)
    return discussion_details


def _fetch_discussion_details(lecture: Lecture, phase: str) -> Any:
    """
    Récupère les amendements à discuter, dans l'ordre de passage

    NB : les amendements jugés irrecevables ne sont pas inclus.
    """
    assert phase in ("commission", "seance")

    url = f"{BASE_URL}/en{phase}/{lecture.session}/{lecture.num_texte}/liste_discussion.json"  # noqa

    resp = requests.get(url)
    if resp.status_code == HTTPStatus.NOT_FOUND:  # 404
        raise NotFound(url)

    data = resp.json()
    return data


def parse_discussion_details(
    uid_map: Dict[str, int], amend: dict, position: int
) -> DiscussionDetails:
    num, rectif = Amendement.parse_num(amend["num"])
    details = DiscussionDetails(
        num=num,
        position=position,
        discussion_commune=(
            int(amend["idDiscussionCommune"])
            if parse_bool(amend["isDiscussionCommune"])
            else None
        ),
        identique=parse_bool(amend["isIdentique"]),
        parent_num=get_parent_num(uid_map, amend),
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
        return uid_map[amend["idAmendementPere"]]
    else:
        return None
