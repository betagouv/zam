import csv
import logging
import re
from collections import OrderedDict

from datetime import datetime
from http import HTTPStatus
from urllib.parse import urlparse
from typing import Dict, Iterable, List, Optional, Tuple

import requests

from zam_repondeur.clean import clean_html
from zam_repondeur.fetch.amendements import FetchResult, RemoteSource
from zam_repondeur.fetch.dates import parse_date
from zam_repondeur.fetch.division import _parse_subdiv
from zam_repondeur.fetch.exceptions import NotFound
from zam_repondeur.fetch.senat.senateurs import fetch_and_parse_senateurs, Senateur
from zam_repondeur.models import Article, Amendement, Lecture, get_one_or_create

from .derouleur import DiscussionDetails, fetch_and_parse_discussion_details


logger = logging.getLogger(__name__)


BASE_URL = "https://www.senat.fr"


class Senat(RemoteSource):
    def fetch(self, lecture: Lecture) -> FetchResult:
        logger.info("Récupération des amendements déposés sur %r", lecture)
        created = 0
        amendements: List[Amendement] = []

        # Remember previous positions and reset them
        old_positions = {}
        for amendement in lecture.amendements:
            old_positions[amendement.num] = amendement.position
            amendement.position = None

        try:
            amendements_created = self._fetch_and_parse_all(lecture=lecture)
        except NotFound:
            return FetchResult(amendements, created, [])

        for amendement, created_ in amendements_created:
            created += int(created_)
            amendements.append(amendement)

        processed_amendements = list(
            self._process_amendements(amendements=amendements, lecture=lecture)
        )

        # Log amendements no longer discussed
        for amdt in lecture.amendements:
            if amdt.position is None and old_positions.get(amdt.num) is not None:
                logger.info("Amendement %s retiré de la discussion", amdt.num)

        return FetchResult(processed_amendements, created, [])

    def _fetch_and_parse_all(self, lecture: Lecture) -> List[Tuple[Amendement, bool]]:
        return [
            self.parse_from_csv(row, lecture)
            for row in _fetch_all(lecture)
            if lecture.partie == parse_partie(row["Numéro "])
        ]

    def parse_from_csv(self, row: dict, lecture: Lecture) -> Tuple[Amendement, bool]:
        subdiv = _parse_subdiv(row["Subdivision "])
        article, _ = get_one_or_create(
            Article,
            lecture=lecture,
            type=subdiv.type_,
            num=subdiv.num,
            mult=subdiv.mult,
            pos=subdiv.pos,
        )
        num, rectif = Amendement.parse_num(row["Numéro "])
        amendement, created = get_one_or_create(
            Amendement, create_kwargs={"article": article}, lecture=lecture, num=num
        )

        modified = self.update_attributes(
            amendement,
            article=article,
            rectif=rectif,
            alinea=row["Alinéa"].strip(),
            auteur=row["Auteur "],
            matricule=extract_matricule(row["Fiche Sénateur"]),
            date_depot=parse_date(row["Date de dépôt "]),
            sort=row["Sort "],
            corps=clean_html(row["Dispositif "]),
            expose=clean_html(row["Objet "]),
        )

        if not created and modified:
            amendement.modified_at = datetime.utcnow()

        return amendement, created

    def _process_amendements(
        self, amendements: Iterable[Amendement], lecture: Lecture
    ) -> Iterable[Amendement]:

        # Les amendements discutés en séance, par ordre de passage
        logger.info(
            "Récupération des amendements soumis à la discussion sur %r", lecture
        )

        discussion_details = fetch_and_parse_discussion_details(
            lecture=lecture, phase="seance"
        )
        if len(discussion_details) == 0:
            logger.info("Aucun amendement soumis à la discussion pour l'instant!")
        self._enrich_discussion_details(amendements, discussion_details, lecture)

        logger.info("Récupération de la liste des sénateurs...")
        senateurs_by_matricule = fetch_and_parse_senateurs()
        self._enrich_groupe_parlementaire(amendements, senateurs_by_matricule)

        return _sort(amendements)

    def _enrich_discussion_details(
        self,
        amendements: Iterable[Amendement],
        discussion_details: Iterable[DiscussionDetails],
        lecture: Lecture,
    ) -> None:
        """
        Enrichir les amendements avec les informations du dérouleur

        - discussion commune ?
        - amendement identique ?
        """
        discussion_details_by_num = {
            details.num: details for details in discussion_details
        }
        for amendement in amendements:
            self._enrich_one(amendement, discussion_details_by_num.get(amendement.num))

    def _enrich_one(
        self, amendement: Amendement, discussion_details: Optional[DiscussionDetails]
    ) -> None:
        if discussion_details is None:
            return
        parent: Optional[Amendement]
        if discussion_details.parent_num is not None:
            parent = Amendement.get(
                lecture=amendement.lecture, num=discussion_details.parent_num
            )
        else:
            parent = None
        self.update_attributes(
            amendement,
            position=discussion_details.position,
            id_discussion_commune=discussion_details.id_discussion_commune,
            id_identique=discussion_details.id_identique,
            parent=parent,
        )

    def _enrich_groupe_parlementaire(
        self,
        amendements: Iterable[Amendement],
        senateurs_by_matricule: Dict[str, Senateur],
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


def aspire_senat(lecture: Lecture) -> FetchResult:
    source = Senat()
    return source.fetch(lecture)


def parse_partie(numero: str) -> Optional[int]:
    if numero.startswith("I-"):
        return 1
    if numero.startswith("II-"):
        return 2
    return None


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
    lines = [_filter_line(line) for line in text.splitlines()[1:]]
    reader = csv.DictReader(lines, delimiter="\t")
    items = list(reader)
    return items


def _filter_line(line: str) -> str:
    """
    Fix buggy TSVs with unescaped tabs around a <link> tag in an HTML cell
    """
    filtered_line, count = re.subn(r"\t?(<link .*?>)\t?", r" \1 ", line)
    return filtered_line


FICHE_RE = re.compile(r"^[\w\/_]+(\d{5}[\da-z])\.html$")


def extract_matricule(url: str) -> Optional[str]:
    if url == "":
        return None
    mo = FICHE_RE.match(urlparse(url).path)
    if mo is not None:
        return mo.group(1).upper()
    raise ValueError(f"Could not extract matricule from '{url}'")


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
