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

    logging.getLogger().setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

    with bootstrap(args.config_uri, options={"app": "zam_fetch_amendements"}):

        repository.load_data()

        try:
            fetch_amendements(args.chambre, args.num)
        finally:
            transaction.abort()


def parse_args(argv: List[str]) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("config_uri")
    parser.add_argument("--chambre", choices=["an", "senat"], required=False)
    parser.add_argument("--num", type=int, required=False)
    return parser.parse_args(argv)


def fetch_amendements(chambre: Optional[str], num: Optional[int]) -> None:
    uids = repository.list_opendata_dossiers()
    bar = ProgressBar(total=len(uids))
    random.shuffle(uids)
    for uid in uids:
        dossier_ref = repository.get_opendata_dossier_ref(uid)
        fetch_amendements_for_dossier(dossier_ref, chambre, num)
        bar.update(step=len(dossier_ref.lectures))


def fetch_amendements_for_dossier(
    dossier_ref: DossierRef, chambre: Optional[str], num: Optional[int]
) -> None:
    dossier, _ = get_one_or_create(
        Dossier,
        uid=dossier_ref.uid,
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
        fetch_amendements_for_lecture(lecture)


def fetch_amendements_for_lecture(lecture: Lecture) -> None:
    chambre = lecture.texte.chambre
    source: RemoteSource = RemoteSource.get_remote_source_for_chambre(chambre)
    try:
        source.fetch(lecture)
    except Exception:
        logger.exception(f"Error while fetching {lecture}")
