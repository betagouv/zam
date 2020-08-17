import logging
import random
import sys
from argparse import ArgumentParser, Namespace
from typing import Any, Dict, List, Optional

import transaction
from progressist import ProgressBar
from pyramid.paster import bootstrap, setup_logging

from zam_repondeur.models import Dossier, Lecture, Texte, get_one_or_create
from zam_repondeur.services.data import repository
from zam_repondeur.services.fetch.amendements import RemoteSource
from zam_repondeur.services.fetch.an.dossiers.models import DossierRef
from zam_repondeur.utils import Timer

logger = logging.getLogger(__name__)


def main(argv: List[str] = sys.argv) -> None:

    args = parse_args(argv[1:])

    setup_logging(args.config_uri)

    log_level = logging.WARNING
    if args.verbose:
        log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG
    logging.getLogger().setLevel(log_level)
    logging.getLogger("urllib3.connectionpool").setLevel(log_level)

    with bootstrap(args.config_uri, options={"app": "zam_fetch_amendements"}) as env:
        settings = env["registry"].settings

        repository.load_data()

        try:
            fetch_amendements(args.chambre, args.num, args.progress, settings)
        finally:
            transaction.abort()


def parse_args(argv: List[str]) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("config_uri")
    parser.add_argument("--chambre", choices=["an", "senat"], required=False)
    parser.add_argument("--num", type=int, required=False, help="N° de texte")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("--no-progress", dest="progress", action="store_false")
    return parser.parse_args(argv)


def fetch_amendements(
    chambre: Optional[str], num: Optional[int], progress: bool, settings: Dict[str, Any]
) -> None:
    an_ids = repository.list_opendata_dossiers()
    if progress:
        bar = ProgressBar(total=len(an_ids))
    random.shuffle(an_ids)
    for an_id in an_ids:
        dossier_ref = repository.get_opendata_dossier_ref(an_id)
        fetch_amendements_for_dossier(dossier_ref, chambre, num, settings)
        if progress:
            bar.update(step=len(dossier_ref.lectures))


def fetch_amendements_for_dossier(
    dossier_ref: DossierRef,
    chambre: Optional[str],
    num: Optional[int],
    settings: Dict[str, Any],
) -> None:
    dossier, _ = get_one_or_create(
        Dossier,
        an_id=dossier_ref.uid,
        create_kwargs=dict(titre=dossier_ref.titre, slug=dossier_ref.slug),
    )
    for lecture_ref in dossier_ref.lectures:
        texte_ref = lecture_ref.texte
        if chambre is not None and texte_ref.chambre.name.lower() != chambre:
            continue
        if num is not None and texte_ref.numero != num:
            continue
        texte, _ = get_one_or_create(
            Texte,
            type_=texte_ref.type_,
            chambre=texte_ref.chambre,
            legislature=texte_ref.legislature,
            session=texte_ref.session,
            numero=texte_ref.numero,
            date_depot=texte_ref.date_depot,
        )
        lecture = Lecture.create(
            phase=lecture_ref.phase,
            dossier=dossier,
            texte=texte,
            partie=lecture_ref.partie,
            organe=lecture_ref.organe,
            titre=lecture_ref.titre,
        )
        fetch_amendements_for_lecture(lecture, settings)


def fetch_amendements_for_lecture(lecture: Lecture, settings: Dict[str, Any]) -> None:
    chambre = lecture.texte.chambre
    source = RemoteSource.get_remote_source_for_chambre(
        chambre=chambre, settings=settings
    )
    if source is None:
        return
    try:
        with Timer() as prepare_timer:
            source.prepare(lecture)
        logger.info("Time to prepare: %.1fs", prepare_timer.elapsed())

        with Timer() as collect_timer:
            changes = source.collect_changes(lecture)
        logger.info("Time to collect: %.1fs", collect_timer.elapsed())

        with Timer() as apply_timer:
            source.apply_changes(lecture, changes)
        logger.info("Time to apply: %.1fs", apply_timer.elapsed())

        logger.info(
            "Total time: %.1fs",
            sum(t.elapsed() for t in (prepare_timer, collect_timer, apply_timer)),
        )
    except Exception:
        logger.exception(f"Error while fetching {lecture}")
