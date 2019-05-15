import logging
from http import HTTPStatus
from typing import Any, Dict, Iterable, Iterator, List, NamedTuple, Optional

import requests

from zam_repondeur.models import Amendement, Lecture


BASE_URL = "https://www.senat.fr"


logger = logging.getLogger(__name__)


class DiscussionDetails(NamedTuple):
    num: int
    position: int
    id_discussion_commune: Optional[int]
    id_identique: Optional[int]
    parent_num: Optional[int]


def fetch_and_parse_discussion_details(
    lecture: Lecture, phase: str
) -> List[DiscussionDetails]:
    data_iter = _fetch_discussion_details(lecture, phase)
    return _parse_derouleur_data(data_iter)


def _fetch_discussion_details(lecture: Lecture, phase: str) -> Iterator[Any]:
    """
    Récupère les amendements à discuter, dans l'ordre de passage

    NB : les amendements jugés irrecevables ne sont pas inclus.
    """
    assert phase in ("commission", "seance")

    for url in derouleur_urls(lecture, phase):
        resp = requests.get(url)
        if resp.status_code == HTTPStatus.NOT_FOUND:  # 404
            logger.warning(f"Could not fetch {url}")
            continue
        yield resp.json()


def _parse_derouleur_data(data_iter: Iterable[Any]) -> List[DiscussionDetails]:
    subdivs_amends = [
        (subdiv, amend)
        for data in data_iter
        for subdiv in data["Subdivisions"]
        for amend in subdiv["Amendements"]
    ]

    uid_map: Dict[str, int] = {
        amend["idAmendement"]: Amendement.parse_num(amend["num"])[0]
        for _, amend in subdivs_amends
    }

    discussion_details = [
        parse_discussion_details(uid_map, amend, position)
        for position, (subdiv, amend) in enumerate(subdivs_amends, start=1)
    ]

    return discussion_details


# Special case for PLF 2019
# cf. http://www.senat.fr/ordre-du-jour/files/Calendrier_budgetaire_PLF2019.pdf
IDTXTS = {
    "2018-2019": {
        146: {
            1: [103393],
            2: [
                103427,  # Mission Économie
                103411,  # Compte spécial - Prêts et avances à des particuliers ou à des organismes privés  # noqa
                103440,  # Mission Remboursements et dégrèvements
                103428,  # Mission Engagements financiers de l'État
                103407,  # Compte spécial - Participation de la France au désendettement de la Grèce  # noqa
                103408,  # Compte spécial - Participations financières de l'État
                103397,  # Compte spécial - Accords monétaires internationaux
                103399,  # Compte spécial - Avances à divers services de l'État ou organismes gérant des services publics  # noqa
                103432,  # Mission Investissements d'avenir
                103420,  # Mission Cohésion des territoires
                103416,  # Mission Administration générale et territoriale de l'État
                103419,  # Mission Anciens combattants, mémoire et liens avec la nation
                103433,  # Mission Justice
                103417,  # Mission Agriculture, alimentation, forêt et affaires rurales
                103403,  # Compte spécial - Développement agricole et rural
                103424,  # Mission Défense
                103426,  # Mission Écologie, développement et mobilité durables
                103395,  # Budget annexe - Contrôle et exploitation aériens
                103398,  # Compte spécial - Aides à l'acquisition de véhicules propres
                103404,  # Compte spécial - Financement des aides aux collectivités pour l'électrification rurale  # noqa
                103412,  # Compte spécial - Services nationaux de transport conventionnés de voyageurs  # noqa
                103413,  # Compte spécial - Transition énergétique
                103444,  # Mission Sport, jeunesse et vie associative
                103435,  # Mission Outre-mer
                103418,  # Mission Aide publique au développement
                103410,  # Compte spécial - Prêts à des États étrangers
                103415,  # Mission Action extérieure de l'État
                103437,  # Mission Recherche et enseignement supérieur
                103423,  # Mission Culture
                103434,  # Mission Médias, livre et industries culturelles
                103400,  # Compte spécial - Avances à l'audiovisuel public
                103436,  # Mission Pouvoirs publics
                103421,  # Mission Conseil et contrôle de l'État
                103425,  # Mission Direction de l'action du Gouvernement
                103396,  # Budget annexe - Publications officielles et information administrative  # noqa
                103445,  # Mission Travail et emploi
                103405,  # Compte spécial - Financement national du développement et de la modernisation de l'apprentissage  # noqa
                103439,  # Mission Relations avec les collectivités territoriales
                103401,  # Compte spécial - Avances aux collectivités territoriales
                103429,  # Mission Enseignement scolaire
                103443,  # Mission Solidarité, insertion et égalité des chances
                103441,  # Mission Santé
                103430,  # Mission Gestion des finances publiques et des ressources humaines  # noqa
                103422,  # Mission Crédits non répartis
                103414,  # Mission Action et transformation publiques
                103406,  # Compte spécial - Gestion du patrimoine immobilier de l'État
                103438,  # Mission Régimes sociaux et de retraite
                103409,  # Compte spécial - Pensions
                103431,  # Mission Immigration, asile et intégration
                103442,  # Mission Sécurités
                103402,  # Compte spécial - Contrôle de la circulation et du stationnement routiers  # noqa
                103394,  # Articles non rattachés
            ],
        }
    }
}


def derouleur_urls(lecture: Lecture, phase: str) -> Iterator[str]:
    idtxts = (
        IDTXTS.get(lecture.session, {})
        .get(lecture.texte.numero, {})
        .get(lecture.partie)
    )
    if idtxts is not None:
        for idtxt in idtxts:
            yield (
                f"{BASE_URL}/en{phase}/{lecture.session}/{lecture.texte.numero}"
                f"/liste_discussion_{idtxt}.json"
            )
    else:
        yield (
            f"{BASE_URL}/en{phase}/{lecture.session}/{lecture.texte.numero}"
            f"/liste_discussion.json"
        )


def parse_discussion_details(
    uid_map: Dict[str, int], amend: dict, position: int
) -> DiscussionDetails:
    num, rectif = Amendement.parse_num(amend["num"])
    details = DiscussionDetails(
        num=num,
        position=position,
        id_discussion_commune=(
            int(amend["idDiscussionCommune"])
            if parse_bool(amend["isDiscussionCommune"])
            else None
        ),
        id_identique=(
            int(amend["idIdentique"]) if parse_bool(amend["isIdentique"]) else None
        ),
        parent_num=get_parent_num(uid_map, amend),
    )
    return details


def parse_bool(text: str) -> bool:
    if text == "true":
        return True
    if text == "false":
        return False
    raise ValueError


def get_parent_num(uid_map: Dict[str, int], amend: dict) -> Optional[int]:
    if (
        "isSousAmendement" in amend
        and parse_bool(amend["isSousAmendement"])
        and "idAmendementPere" in amend
    ):
        return uid_map[amend["idAmendementPere"]]
    else:
        return None
