import logging
import random
import sys
from argparse import ArgumentParser, Namespace
from typing import List, Optional

import transaction
from progressist import ProgressBar
from pyramid.paster import get_appsettings, setup_logging
from sqlalchemy import engine_from_config

from zam_repondeur import BASE_SETTINGS
from zam_repondeur.data import init_repository, repository
from zam_repondeur.dossiers import get_dossiers_legislatifs_open_data_from_cache
from zam_repondeur.fetch.amendements import RemoteSource
from zam_repondeur.fetch.an.dossiers.models import DossierRef
from zam_repondeur.models import DBSession, Dossier, Lecture, Texte, get_one_or_create


logger = logging.getLogger(__name__)


def main(argv: List[str] = sys.argv) -> None:

    args = parse_args(argv[1:])

    setup_logging(args.config_uri)

    logging.getLogger().setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

    settings = get_appsettings(args.config_uri)
    settings = {**BASE_SETTINGS, **settings}

    engine = engine_from_config(
        settings, "sqlalchemy.", connect_args={"application_name": "zam_worker"}
    )

    DBSession.configure(bind=engine)

    init_repository(settings)
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
    dossier_refs_dict = get_dossiers_legislatifs_open_data_from_cache()
    dossier_refs: List[DossierRef] = list(dossier_refs_dict.values())
    bar = ProgressBar(
        total=sum(len(dossier_ref.lectures) for dossier_ref in dossier_refs)
    )
    random.shuffle(dossier_refs)
    for dossier_ref in dossier_refs:
        fetch_amendements_for_dossier(dossier_ref, chambre, num)
        bar.update(step=len(dossier_ref.lectures))


def fetch_amendements_for_dossier(
    dossier_ref: DossierRef, chambre: Optional[str], num: Optional[int]
) -> None:
    dossier = Dossier.create(uid=dossier_ref.uid, titre=dossier_ref.titre)
    for lecture_ref in dossier_ref.lectures:
        texte_ref = lecture_ref.texte
        if chambre is not None and texte_ref.chambre.value != chambre:
            continue
        if num is not None and texte_ref.numero != num:
            continue
        texte, _ = get_one_or_create(
            Texte,
            create_kwargs=dict(
                type_=texte_ref.type_,
                chambre=texte_ref.chambre,
                legislature=texte_ref.legislature,
                session=texte_ref.session,
                numero=texte_ref.numero,
                date_depot=texte_ref.date_depot,
            ),
        )
        lecture = Lecture.create(
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
