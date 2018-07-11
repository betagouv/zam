"""
Récupérer la liste des amendements relatifs à un texte de loi.
"""
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

import zam_aspirateur.amendements.fetch_senat as senat
from zam_aspirateur.amendements.models import Amendement
from zam_aspirateur.senateurs.fetch import fetch_senateurs
from zam_aspirateur.senateurs.models import Senateur
from zam_aspirateur.senateurs.parse import parse_senateurs


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
