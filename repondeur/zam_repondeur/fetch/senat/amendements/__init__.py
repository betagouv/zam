import csv
from collections import OrderedDict
from http import HTTPStatus
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

import requests

from zam_repondeur.fetch.exceptions import NotFound
from zam_repondeur.models import Amendement, Lecture
from zam_repondeur.fetch.senat.senateurs import fetch_and_parse_senateurs, Senateur

from .parse import parse_from_csv, parse_from_json


BASE_URL = "https://www.senat.fr"


def aspire_senat(lecture: Lecture) -> Tuple[List[Amendement], int]:
    print("Récupération des amendements déposés...")
    created = 0
    amendements: List[Amendement] = []
    try:
        amendements_created = _fetch_and_parse_all(lecture=lecture)
    except NotFound:
        return amendements, created

    for amendement, created_ in amendements_created:
        created += int(created_)
        amendements.append(amendement)

    processed_amendements = _process_amendements(
        amendements=amendements, lecture=lecture
    )
    return list(processed_amendements), created


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
    print("Récupération des amendements soumis à la discussion...")
    amendements_derouleur = _fetch_and_parse_discussed(lecture=lecture, phase="seance")
    if len(amendements_derouleur) == 0:
        print("Aucun amendement soumis à la discussion pour l'instant!")

    print("Récupération de la liste des sénateurs...")
    senateurs_by_matricule = fetch_and_parse_senateurs()

    amendements_avec_groupe = _enrich_groupe_parlementaire(
        amendements, senateurs_by_matricule
    )

    return _sort(
        _enrich(amendements_avec_groupe, amendements_derouleur), amendements_derouleur
    )


def _fetch_and_parse_discussed(lecture: Lecture, phase: str) -> List[Amendement]:
    try:
        data = _fetch_discussed(lecture, phase)
    except NotFound:
        return []
    subdivs_amends = [
        (subdiv, amend)
        for subdiv in data["Subdivisions"]
        for amend in subdiv["Amendements"]
    ]
    uid_map: Dict[str, Amendement] = {}
    amendements = []
    for position, (subdiv, amend) in enumerate(subdivs_amends, start=1):
        amendement = parse_from_json(uid_map, amend, position, lecture, subdiv)
        uid_map[amend["idAmendement"]] = amendement
        amendements.append(amendement)
    return amendements


def _fetch_discussed(lecture: Lecture, phase: str) -> Any:
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
) -> Iterator[Amendement]:
    """
    Enrichir les amendements avec le groupe parlementaire de l'auteur
    """
    for amendement in amendements:
        amendement.groupe = (
            senateurs_by_matricule[amendement.matricule].groupe
            if amendement.matricule is not None
            else ""
        )
        yield amendement


def _enrich(
    amendements: Iterable[Amendement], amendements_derouleur: Iterable[Amendement]
) -> Iterator[Amendement]:
    """
    Enrichir les amendements avec les informations du dérouleur

    - discussion commune ?
    - amendement identique ?
    """
    amendements_discussion_by_num = {
        amend.num: amend for amend in amendements_derouleur
    }
    return (
        _enrich_one(amend, amendements_discussion_by_num.get(amend.num))
        for amend in amendements
    )


def _enrich_one(
    amend: Amendement, amend_discussion: Optional[Amendement]
) -> Amendement:
    if amend_discussion is None:
        return amend
    amend.position = amend_discussion.position
    amend.discussion_commune = amend_discussion.discussion_commune
    amend.identique = amend_discussion.identique
    amend.parent = amend_discussion.parent
    return amend


def _sort(
    amendements: Iterable[Amendement], amendements_derouleur: Iterable[Amendement]
) -> List[Amendement]:
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
