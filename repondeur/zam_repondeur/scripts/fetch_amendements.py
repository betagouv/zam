import logging
import random
import sys
from argparse import ArgumentParser, Namespace
from typing import List, Optional

import transaction
from progressist import ProgressBar
from pyramid.paster import bootstrap, setup_logging

from zam_repondeur.models import Dossier, Lecture, Texte, get_one_or_create
from zam_repondeur.services.data import repository
from zam_repondeur.services.fetch.amendements import RemoteSource
from zam_repondeur.services.fetch.an.dossiers.models import DossierRef

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

    with bootstrap(args.config_uri, options={"app": "zam_fetch_amendements"}):

        logger.info("=" * 80)
        logger.info("Refreshing data in Redis cache")
        logger.info("=" * 80)
        repository.load_data()
        logger.info("")

        try:
            success = fetch_amendements(args.chambre, args.num_texte, args.limit)
            if success:
                sys.exit(0)
        finally:
            transaction.abort()
    sys.exit(1)


def parse_args(argv: List[str]) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("config_uri")
    parser.add_argument("--chambre", choices=["an", "senat"], required=False)
    parser.add_argument("--num-texte", type=int, required=False)
    parser.add_argument("--limit", type=int, required=False)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args(argv)


def fetch_amendements(
    chambre: Optional[str], num_texte: Optional[int], limit: Optional[int]
) -> bool:
    success = True
    uids = repository.list_opendata_dossiers()
    nb_to_fetch = limit or len(uids)
    bar = ProgressBar(total=nb_to_fetch)
    for uid in random.sample(uids, nb_to_fetch):
        dossier_ref = repository.get_opendata_dossier(uid)
        if dossier_ref.lectures:
            logger.info("=" * 80)
            logger.info("%s (%s)", dossier_ref.titre, dossier_ref.uid)
            logger.info("%s", dossier_ref.an_url)
            logger.info("=" * 80)
            if not fetch_amendements_for_dossier(dossier_ref, chambre, num_texte):
                success = False
            logger.info("")
        bar.update(step=len(dossier_ref.lectures))
    return success


def fetch_amendements_for_dossier(
    dossier_ref: DossierRef, chambre: Optional[str], num_texte: Optional[int]
) -> bool:
    success = True
    dossier, _ = get_one_or_create(
        Dossier,
        uid=dossier_ref.uid,
        create_kwargs=dict(titre=dossier_ref.titre, slug=dossier_ref.slug),
    )
    for lecture_ref in dossier_ref.lectures:
        texte_ref = lecture_ref.texte
        if chambre is not None and texte_ref.chambre.name.lower() != chambre:
            continue
        if num_texte is not None and texte_ref.numero != num_texte:
            continue
        logger.info("\t" + "-" * 80)
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
        if not fetch_amendements_for_lecture(lecture):
            success = False
    return success


def fetch_amendements_for_lecture(lecture: Lecture) -> bool:
    chambre = lecture.texte.chambre
    source: RemoteSource = RemoteSource.get_remote_source_for_chambre(chambre)
    try:
        result = source.fetch(lecture)
        return not result.errored
    except Exception:
        logger.exception(f"Error while fetching {lecture}")
        return False
