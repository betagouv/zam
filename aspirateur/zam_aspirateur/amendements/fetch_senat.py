import csv
from collections import OrderedDict
from http import HTTPStatus
from typing import Any, List
from urllib.parse import urljoin

import requests
from selectolax.parser import HTMLParser

from ..exceptions import NotFound
from .models import Amendement
from .parser import parse_from_csv, parse_from_json


BASE_URL = "http://www.senat.fr"


def fetch_title(session: str, num: str) -> str:
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


def fetch_all(session: str, num: str) -> List[OrderedDict]:
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


def fetch_and_parse_all(session: str, num: str) -> List[Amendement]:
    return [parse_from_csv(row, session, num) for row in fetch_all(session, num)]


def fetch_discussed(session: str, num: str, phase: str) -> Any:
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


def fetch_and_parse_discussed(session: str, num: str, phase: str) -> List[Amendement]:
    try:
        data = fetch_discussed(session, num, phase)
    except NotFound:
        return []
    return [
        parse_from_json(amend, position, session, num, subdiv)
        for position, (subdiv, amend) in enumerate(
            (
                (subdiv, amend)
                for subdiv in data["Subdivisions"]
                for amend in subdiv["Amendements"]
            ),
            start=1,
        )
    ]
