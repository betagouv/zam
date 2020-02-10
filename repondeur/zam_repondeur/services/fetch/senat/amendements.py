import csv
import logging
import re
import sys
from collections import OrderedDict
from http import HTTPStatus
from typing import Iterable, List, Optional, Set, Tuple
from urllib.parse import urlparse

from zam_repondeur.models import Amendement, Chambre, Lecture
from zam_repondeur.services.clean import clean_html
from zam_repondeur.services.data import repository
from zam_repondeur.services.fetch.amendements import (
    CollectedChanges,
    FetchResult,
    RemoteSource,
)
from zam_repondeur.services.fetch.dates import parse_date
from zam_repondeur.services.fetch.division import parse_subdiv
from zam_repondeur.services.fetch.exceptions import NotFound
from zam_repondeur.services.fetch.http import get_http_session
from zam_repondeur.utils import Timer

from .derouleur import DiscussionDetails, fetch_and_parse_discussion_details

logger = logging.getLogger(__name__)

BASE_URL = "https://www.senat.fr"
# To deal with potentially very long lines in the CSV file (like 166k chars).
# https://www.senat.fr/amendements/2019-2020/139/jeu_complet_2019-2020_139.csv
csv.field_size_limit(sys.maxsize)


class Senat(RemoteSource):
    def prepare(self, lecture: Lecture) -> None:
        if self.prefetching_enabled:
            logger.info("Préchargement des amendements de %r", lecture)
            with Timer() as timer:
                self._fetch(lecture, dry_run=True)
            logger.info("Temps de préchargement : %.1fs", timer.elapsed())

    def collect_changes(
        self, lecture: Lecture, start_index: int = 0
    ) -> CollectedChanges:
        # TODO: split into separate collect_changes/apply_changes like AN
        return CollectedChanges.create()

    def apply_changes(self, lecture: Lecture, changes: CollectedChanges) -> FetchResult:
        # TODO: split into separate collect_changes/apply_changes like AN
        return self._fetch(lecture)

    def _fetch(self, lecture: Lecture, dry_run: bool = False) -> FetchResult:
        created: Set[int] = set()
        amendements: List[Amendement] = []

        # Remember previous positions and reset them
        old_positions = {}
        for amendement in lecture.amendements:
            old_positions[amendement.num] = amendement.position
            amendement.position = None

        try:
            amendements_created = self._fetch_and_parse_all(
                lecture=lecture, dry_run=dry_run
            )
        except NotFound:
            return FetchResult.create(amendements=set(), created=set())

        for amendement, created_ in amendements_created:
            if created_:
                created.add(amendement.num)
            amendements.append(amendement)

        processed_amendements = list(
            self._process_amendements(amendements=amendements, lecture=lecture)
        )
        lecture.reset_fetch_progress()

        # Log amendements no longer discussed
        for amdt in lecture.amendements:
            if amdt.position is None and old_positions.get(amdt.num) is not None:
                logger.info("Amendement %s retiré de la discussion", amdt.num)

        return FetchResult.create(
            amendements={amdt.num for amdt in processed_amendements}, created=created
        )

    def _fetch_and_parse_all(
        self, lecture: Lecture, dry_run: bool = False
    ) -> List[Tuple[Amendement, bool]]:
        return [
            self.parse_from_csv(row, lecture)
            for row in _fetch_all(lecture, dry_run)
            if lecture.partie == parse_partie(row["Numéro "])
        ]

    def parse_from_csv(self, row: dict, lecture: Lecture) -> Tuple[Amendement, bool]:
        subdiv = parse_subdiv(row["Subdivision "], texte=lecture.texte)
        article, _ = lecture.find_or_create_article(subdiv)

        num, rectif = Amendement.parse_num(row["Numéro "])
        amendement, created = lecture.find_or_create_amendement(num, article)

        self.update_rectif(amendement, rectif)
        self.update_corps(amendement, clean_html(row["Dispositif "]))
        self.update_expose(amendement, clean_html(row["Objet "]))
        self.update_sort(amendement, row["Sort "])
        self.update_attributes(
            amendement,
            article=article,
            alinea=row["Alinéa"].strip(),
            auteur=row["Auteur "],
            matricule=extract_matricule(row["Fiche Sénateur"]),
            date_depot=parse_date(row["Date de dépôt "]),
        )

        return amendement, created

    def _process_amendements(
        self, amendements: Iterable[Amendement], lecture: Lecture
    ) -> Iterable[Amendement]:

        # Les amendements discutés en séance, par ordre de passage
        logger.info(
            "Récupération des amendements soumis à la discussion sur %r", lecture
        )

        discussion_details = fetch_and_parse_discussion_details(lecture=lecture)
        if len(discussion_details) == 0:
            logger.info("Aucun amendement soumis à la discussion pour l'instant!")
        self._enrich_discussion_details(amendements, discussion_details, lecture)
        self._enrich_groupe_parlementaire(amendements)

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

        mission_ref = discussion_details.mission_ref
        self.update_attributes(
            amendement,
            position=discussion_details.position,
            id_discussion_commune=discussion_details.id_discussion_commune,
            id_identique=discussion_details.id_identique,
            parent=parent,
            mission_titre=mission_ref.titre if mission_ref else None,
            mission_titre_court=mission_ref.titre_court if mission_ref else None,
        )

    def _enrich_groupe_parlementaire(self, amendements: Iterable[Amendement]) -> None:
        """
        Enrichir les amendements avec le groupe parlementaire de l'auteur
        """
        for amendement in amendements:
            amendement.groupe = ""
            if amendement.matricule is not None:
                senateur = repository.get_senateur(amendement.matricule)
                if senateur:
                    amendement.groupe = senateur.groupe


def parse_partie(numero: str) -> Optional[int]:
    if numero.startswith("I-"):
        return 1
    if numero.startswith("II-"):
        return 2
    return None


def _fetch_all(lecture: Lecture, dry_run: bool = False) -> List[OrderedDict]:
    """
    Récupère tous les amendements, dans l'ordre de dépôt
    """

    http_session = get_http_session()
    url = _build_amendements_url(lecture)
    resp = http_session.get(url)
    if resp.status_code == HTTPStatus.NOT_FOUND:
        raise NotFound(url)

    if dry_run:
        return []

    text = resp.content.decode("cp1252")
    lines = [_filter_line(line) for line in text.splitlines()[1:]]
    reader = csv.DictReader(lines, delimiter="\t")
    items = list(reader)
    return items


def _build_amendements_url(lecture: Lecture) -> str:
    if lecture.chambre != Chambre.SENAT:
        raise ValueError(f"Invalid chambre {lecture.chambre}")
    texte = lecture.texte
    if lecture.is_commission:
        path = f"/amendements/commissions/{texte.session_str}/{texte.numero}/"
        filename = f"jeu_complet_commission_{texte.session_str}_{texte.numero}.csv"
    else:
        path = f"/amendements/{texte.session_str}/{texte.numero}/"
        filename = f"jeu_complet_{texte.session_str}_{texte.numero}.csv"
    return BASE_URL + path + filename


def _filter_line(line: str) -> str:
    """
    Fix buggy TSVs with unescaped tabs inside the HTML
    """
    chunks = line.split("\t")
    merged_chunks = list(_merge_badly_split_chunks(chunks))
    if len(merged_chunks) != 12:
        raise ValueError(f"Could not parse malformed TSV line: {line!r}")
    filtered_line = "\t".join(merged_chunks)
    return filtered_line


def _merge_badly_split_chunks(chunks: Iterable[str]) -> Iterable[str]:
    chunks = iter(chunks)
    for chunk in chunks:
        while chunk.startswith("<body>") and not chunk.rstrip().endswith("</body>"):
            try:
                chunk += " " + next(chunks)
            except StopIteration:
                break
        yield chunk


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
