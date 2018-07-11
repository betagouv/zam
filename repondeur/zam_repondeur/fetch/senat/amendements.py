import csv
from collections import OrderedDict
from http import HTTPStatus
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple
from urllib.parse import urljoin

import requests
from selectolax.parser import HTMLParser

from zam_aspirateur.amendements.models import Amendement
from zam_aspirateur.amendements.parser import parse_from_csv, parse_from_json
from zam_aspirateur.exceptions import NotFound
from zam_aspirateur.senateurs.fetch import fetch_senateurs
from zam_aspirateur.senateurs.models import Senateur
from zam_aspirateur.senateurs.parse import parse_senateurs


BASE_URL = "https://www.senat.fr"


def aspire_senat(session: str, num: int, organe: str) -> Tuple[str, List[Amendement]]:
    print("Récupération du titre...")
    title = _fetch_title(session, num)

    print("Récupération des amendements déposés...")
    try:
        amendements = _fetch_and_parse_all(session, num, organe)
    except NotFound:
        return "", []

    processed_amendements = _process_amendements(
        amendements=amendements, session=session, num=num, organe=organe
    )
    return title, list(processed_amendements)


def _fetch_title(session: str, num: int) -> str:
    """
    Récupère le titre du projet de loi de puis le site du Sénat.
    """
    url = f"{BASE_URL}/dossiers-legislatifs/depots/depots-{session[:4]}.html"

    resp = requests.get(url)
    if resp.status_code == HTTPStatus.NOT_FOUND:
        raise NotFound(url)

    project_url = None
    for link in HTMLParser(resp.content).css(".flgris span a"):
        if link.text() == f"N°\xa0{num}":
            project_url = link.attributes.get("href")
            break

    if not project_url:
        return "Unknown"

    url = urljoin(BASE_URL, project_url)

    resp = requests.get(url)
    if resp.status_code == HTTPStatus.NOT_FOUND:
        raise NotFound(url)

    title: str = HTMLParser(resp.content).css_first("h1").text()

    return title


def _fetch_and_parse_all(session: str, num: int, organe: str) -> List[Amendement]:
    return [
        parse_from_csv(row, session, num, organe) for row in _fetch_all(session, num)
    ]


def _fetch_all(session: str, num: int) -> List[OrderedDict]:
    """
    Récupère tous les amendements, dans l'ordre de dépôt
    """
    url = f"{BASE_URL}/amendements/{session}/{num}/jeu_complet_{session}_{num}.csv"

    resp = requests.get(url)
    if resp.status_code == HTTPStatus.NOT_FOUND:  # 404
        raise NotFound(url)

    text = resp.content.decode("cp1252")
    lines = text.splitlines()[1:]
    reader = csv.DictReader(lines, delimiter="\t")
    items = list(reader)
    return items


def _process_amendements(
    amendements: Iterable[Amendement], session: str, num: int, organe: str
) -> Iterable[Amendement]:

    # Les amendements discutés en séance, par ordre de passage
    print("Récupération des amendements soumis à la discussion...")
    amendements_derouleur = _fetch_and_parse_discussed(
        session=session, num=num, organe=organe, phase="seance"
    )
    if len(amendements_derouleur) == 0:
        print("Aucun amendement soumis à la discussion pour l'instant!")

    print("Récupération de la liste des sénateurs...")
    senateurs_by_matricule = _fetch_and_parse_senateurs()

    amendements_avec_groupe = _enrich_groupe_parlementaire(
        amendements, senateurs_by_matricule
    )

    return _sort(
        _enrich(amendements_avec_groupe, amendements_derouleur), amendements_derouleur
    )


def _fetch_and_parse_discussed(
    session: str, num: int, organe: str, phase: str
) -> List[Amendement]:
    try:
        data = _fetch_discussed(session, num, phase)
    except NotFound:
        return []
    return [
        parse_from_json(amend, position, session, num, organe, subdiv)
        for position, (subdiv, amend) in enumerate(
            (
                (subdiv, amend)
                for subdiv in data["Subdivisions"]
                for amend in subdiv["Amendements"]
            ),
            start=1,
        )
    ]


def _fetch_discussed(session: str, num: int, phase: str) -> Any:
    """
    Récupère les amendements à discuter, dans l'ordre de passage

    NB : les amendements jugés irrecevables ne sont pas inclus.
    """
    assert phase in ("commission", "seance")

    url = f"{BASE_URL}/en{phase}/{session}/{num}/liste_discussion.json"

    resp = requests.get(url)
    if resp.status_code == HTTPStatus.NOT_FOUND:  # 404
        raise NotFound(url)

    data = resp.json()
    return data


def _fetch_and_parse_senateurs() -> Dict[str, Senateur]:
    lines = fetch_senateurs()
    by_matricule = parse_senateurs(lines)  # type: Dict[str, Senateur]
    return by_matricule


def _enrich_groupe_parlementaire(
    amendements: Iterable[Amendement], senateurs_by_matricule: Dict[str, Senateur]
) -> Iterator[Amendement]:
    """
    Enrichir les amendements avec le groupe parlementaire de l'auteur
    """
    return (
        amendement.replace(
            {
                "groupe": senateurs_by_matricule[amendement.matricule].groupe
                if amendement.matricule is not None
                else ""
            }
        )
        for amendement in amendements
    )


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
    return amend.replace(
        {
            "position": amend_discussion.position,
            "discussion_commune": amend_discussion.discussion_commune,
            "identique": amend_discussion.identique,
        }
    )


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
