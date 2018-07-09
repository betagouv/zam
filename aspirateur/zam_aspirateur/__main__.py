"""
Récupérer la liste des amendements relatifs à un texte de loi.
"""
import argparse
import sys
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, NewType, Optional, Tuple

import zam_aspirateur.amendements.fetch_senat as senat
import zam_aspirateur.amendements.fetch_an as an
from zam_aspirateur.amendements.models import Amendement
from zam_aspirateur.amendements.writer import (
    write_csv,
    write_json_for_viewer,
    write_xlsx,
)
from zam_aspirateur.senateurs.fetch import fetch_senateurs
from zam_aspirateur.senateurs.models import Senateur
from zam_aspirateur.senateurs.parse import parse_senateurs


SystemStatus = NewType("SystemStatus", int)  # status code for sys.exit()


def aspire_senat(
    session: str, num: int, organe: str
) -> Tuple[str, Iterable[Amendement]]:
    print("Récupération du titre...")
    title = senat.fetch_title(session, num)

    print("Récupération des amendements déposés...")
    try:
        amendements = senat.fetch_and_parse_all(session, num, organe)
    except senat.NotFound:
        return "", []

    processed_amendements = process_amendements(
        amendements=amendements, session=session, num=num, organe=organe
    )
    return title, processed_amendements


def aspire_an(
    legislature: int, texte: int, organe: str, groups_folder: Path
) -> Tuple[str, List[Amendement], List[str]]:
    print("Récupération du titre et des amendements déposés...")
    try:
        title, amendements, errored = an.fetch_and_parse_all(
            legislature=legislature,
            texte=texte,
            organe=organe,
            groups_folder=groups_folder,
        )
    except an.NotFound:
        return "", [], []

    return title, amendements, errored


def main(argv: Optional[List[str]] = None) -> SystemStatus:
    args = parse_args(argv=argv)

    if args.source == "senat":
        title, amendements = aspire_senat(
            session=args.session, num=args.texte, organe=args.organe
        )
    elif args.source == "an":
        if args.folder_groups is None:
            print("Le paramètre --folder-groups est requis pour l'assemblée nationale")
            return SystemStatus(1)

        title, amendements, errored = aspire_an(
            legislature=int(args.session),
            texte=int(args.texte),
            organe=args.organe,
            groups_folder=Path(args.folder_groups),
        )
        if errored:
            print(f"Les amendements {', '.join(errored)} n’ont pu être récupérés.")

    if not amendements:
        print("Aucun amendement déposé pour l'instant!")
        return SystemStatus(1)

    format = args.output_format
    default_filename = f"amendements_{args.session}_{args.texte}.{format}"

    save_output(
        title=title,
        amendements=amendements,
        filename=args.output or default_filename,
        format=format,
    )

    return SystemStatus(0)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--session", required=True, help="session parlementaire (p.ex. 2017-2018)"
    )
    parser.add_argument(
        "--texte", required=True, help="numéro du texte au Sénat (p.ex. 330)"
    )
    parser.add_argument("--output", help="nom de fichier de la sortie")
    parser.add_argument(
        "--folder-groups", help="chemin vers les fichiers de détail des groupes"
    )
    parser.add_argument(
        "--source",
        default="senat",
        choices=["senat", "an"],
        help="institution fournissant les données",
    )
    parser.add_argument(
        "--organe",
        default="PO717460",
        help="organe examinant le texte (pour l'Assemblée nationale)",
    )
    parser.add_argument(
        "--output-format",
        default="csv",
        choices=["csv", "xlsx", "json"],
        help="format de sortie à générer",
    )
    return parser.parse_args(argv)


def process_amendements(
    amendements: Iterable[Amendement], session: str, num: int, organe: str
) -> Iterable[Amendement]:

    # Les amendements discutés en séance, par ordre de passage
    print("Récupération des amendements soumis à la discussion...")
    amendements_derouleur = senat.fetch_and_parse_discussed(
        session=session, num=num, organe=organe, phase="seance"
    )
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


def fetch_and_parse_senateurs() -> Dict[str, Senateur]:
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


def save_output(
    title: str, amendements: Iterable[Amendement], filename: str, format: str
) -> None:
    """
    Save amendments

    - as a spreadsheet, either in CSV or XLSX format
    - as a JSON file suitable for opening with the viewer
    """
    if format in ("csv", "xlsx"):
        write_func = write_csv if format == "csv" else write_xlsx
        print("Écriture du tableau...")
        nb_rows = write_func(amendements, filename)
        print(f"{nb_rows} amendements écrits dans {filename}")
    elif format == "json":
        print("Écriture du fichier...")
        nb_rows = write_json_for_viewer(1, title, amendements, filename)
        print(f"{nb_rows} amendements écrits dans {filename}")
    else:
        raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
