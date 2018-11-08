import csv
import logging
from collections import OrderedDict
from http import HTTPStatus
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests

from zam_repondeur.fetch.exceptions import NotFound
from zam_repondeur.models import Amendement, Lecture
from zam_repondeur.fetch.senat.senateurs import fetch_and_parse_senateurs, Senateur

from .parse import DiscussionDetails, parse_from_csv, parse_discussion_details


logger = logging.getLogger(__name__)


BASE_URL = "https://www.senat.fr"


def aspire_senat(lecture: Lecture) -> Tuple[List[Amendement], int]:
    logger.info("Récupération des amendements déposés sur %r", lecture)
    created = 0
    amendements: List[Amendement] = []
    try:
        amendements_created = _fetch_and_parse_all(lecture=lecture)
    except NotFound:
        return amendements, created

    for amendement, created_ in amendements_created:
        created += int(created_)
        amendements.append(amendement)

    processed_amendements = list(
        _process_amendements(amendements=amendements, lecture=lecture)
    )

    return processed_amendements, created


def _fetch_and_parse_all(lecture: Lecture) -> List[Tuple[Amendement, bool]]:
    return [parse_from_csv(row, lecture) for row in _fetch_all(lecture)]


def _fetch_all(lecture: Lecture) -> List[OrderedDict]:
    """
    Récupère tous les amendements, dans l'ordre de dépôt
    """
    # Fallback to commissions.
    urls = [
        f"{BASE_URL}/amendements/{lecture.session}/{lecture.num_texte}/jeu_complet_{lecture.session}_{lecture.num_texte}.csv",  # noqa
        f"{BASE_URL}/amendements/commissions/{lecture.session}/{lecture.num_texte}/jeu_complet_commission_{lecture.session}_{lecture.num_texte}.csv",  # noqa
    ]

    for url in urls:
        resp = requests.get(url)
        if resp.status_code != HTTPStatus.NOT_FOUND:
            break

    if resp.status_code == HTTPStatus.NOT_FOUND:
        raise NotFound(url)

    text = resp.content.decode("cp1252")
    lines = text.splitlines()[1:]
    reader = csv.DictReader(lines, delimiter="\t")
    items = list(reader)
    return items


def _process_amendements(
    amendements: Iterable[Amendement], lecture: Lecture
) -> Iterable[Amendement]:

    # Les amendements discutés en séance, par ordre de passage
    logger.info("Récupération des amendements soumis à la discussion sur %r", lecture)

    discussion_details = _fetch_and_parse_discussion_details(
        lecture=lecture, phase="seance"
    )
    if len(discussion_details) == 0:
        logger.info("Aucun amendement soumis à la discussion pour l'instant!")
    _enrich_discussion_details(amendements, discussion_details, lecture)

    logger.info("Récupération de la liste des sénateurs...")
    senateurs_by_matricule = fetch_and_parse_senateurs()
    _enrich_groupe_parlementaire(amendements, senateurs_by_matricule)

    return _sort(amendements)


def _fetch_and_parse_discussion_details(
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


def _enrich_groupe_parlementaire(
    amendements: Iterable[Amendement], senateurs_by_matricule: Dict[str, Senateur]
) -> None:
    """
    Enrichir les amendements avec le groupe parlementaire de l'auteur
    """
    for amendement in amendements:
        amendement.groupe = (
            senateurs_by_matricule[amendement.matricule].groupe
            if amendement.matricule is not None
            else ""
        )


def _enrich_discussion_details(
    amendements: Iterable[Amendement],
    discussion_details: Iterable[DiscussionDetails],
    lecture: Lecture,
) -> None:
    """
    Enrichir les amendements avec les informations du dérouleur

    - discussion commune ?
    - amendement identique ?
    """
    discussion_details_by_num = {details.num: details for details in discussion_details}
    for amend in amendements:
        _enrich_one(amend, discussion_details_by_num.get(amend.num))

    discussed = {details.num for details in discussion_details}
    for amendement in lecture.amendements:
        if amendement.position is not None and amendement.num not in discussed:
            logger.info("Amendement %s retiré de la discussion", amendement.num)
            amendement.position = None


def _enrich_one(
    amend: Amendement, discussion_details: Optional[DiscussionDetails]
) -> None:
    if discussion_details is None:
        return
    amend.position = discussion_details.position
    amend.discussion_commune = discussion_details.discussion_commune
    amend.identique = discussion_details.identique
    if discussion_details.parent_num is not None:
        amend.parent = Amendement.get(
            lecture=amend.lecture, num=discussion_details.parent_num
        )
    else:
        amend.parent = None


def _sort(amendements: Iterable[Amendement]) -> List[Amendement]:
    """
    Trier les amendements par ordre de passage, puis par numéro
    """
    return sorted(
        amendements,
        key=lambda amendement: (
            1 if amendement.position is None else 0,
            amendement.position,
            amendement.num,
        ),
    )
