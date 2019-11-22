import logging
from typing import Dict, List, NamedTuple, Optional, Tuple

logger = logging.getLogger(__name__)


class MissionRef(NamedTuple):
    titre: str
    titre_court: str


# Special case for PLF 2019
# cf. http://www.senat.fr/ordre-du-jour/files/Calendrier_budgetaire_PLF2019.pdf

Session = str
Texte = int
Partie = Optional[int]
IdTxt = int

ID_TXT_MISSIONS: Dict[
    Session, Dict[Texte, Dict[Partie, List[Tuple[IdTxt, MissionRef]]]]
] = {
    "2019-2020": {139: {1: [(103929, MissionRef(titre="", titre_court=""))]}},
    "2018-2019": {
        146: {
            1: [(103393, MissionRef(titre="", titre_court=""))],
            2: [
                # Missions classiques.
                (
                    103414,
                    MissionRef(
                        titre="Mission Action et transformation publiques",
                        titre_court="Action transfo.",
                    ),
                ),
                (
                    103415,
                    MissionRef(
                        titre="Mission Action extérieure de l'État",
                        titre_court="Action ext.",
                    ),
                ),
                (
                    103416,
                    MissionRef(
                        titre="Mission Administration générale et territoriale de l'État",  # noqa
                        titre_court="Administration",
                    ),
                ),
                (
                    103417,
                    MissionRef(
                        titre="Mission Agriculture, alimentation, forêt et affaires rurales",  # noqa
                        titre_court="Agri. alim.",
                    ),
                ),
                (
                    103418,
                    MissionRef(
                        titre="Mission Aide publique au développement",
                        titre_court="APD",
                    ),
                ),
                (
                    103419,
                    MissionRef(
                        titre="Mission Anciens combattants, mémoire et liens avec la nation",  # noqa
                        titre_court="Anciens combattants",
                    ),
                ),
                (
                    103420,
                    MissionRef(
                        titre="Mission Cohésion des territoires",
                        titre_court="Cohésion terr.",
                    ),
                ),
                (
                    103421,
                    MissionRef(
                        titre="Mission Conseil et contrôle de l'État",
                        titre_court="Conseil et contr.",
                    ),
                ),
                (
                    103422,
                    MissionRef(
                        titre="Mission Crédits non répartis", titre_court="Crédits NR"
                    ),
                ),
                (103423, MissionRef(titre="Mission Culture", titre_court="Culture")),
                (103424, MissionRef(titre="Mission Défense", titre_court="Défense")),
                (
                    103425,
                    MissionRef(
                        titre="Mission Direction de l'action du Gouvernement",
                        titre_court="Action Gouv.",
                    ),
                ),
                (
                    103426,
                    MissionRef(
                        titre="Mission Écologie, développement et mobilité durables",
                        titre_court="Écologie",
                    ),
                ),
                (103427, MissionRef(titre="Mission Économie", titre_court="Économie")),
                (
                    103428,
                    MissionRef(
                        titre="Mission Engagements financiers de l'État",
                        titre_court="Engagements",
                    ),
                ),
                (
                    103429,
                    MissionRef(
                        titre="Mission Enseignement scolaire",
                        titre_court="Enseignement sco.",
                    ),
                ),
                (
                    103430,
                    MissionRef(
                        titre="Mission Gestion des finances publiques et des ressources humaines",  # noqa
                        titre_court="Fi. pub. et RH",
                    ),
                ),
                (
                    103431,
                    MissionRef(
                        titre="Mission Immigration, asile et intégration",
                        titre_court="Immigration",
                    ),
                ),
                (
                    103432,
                    MissionRef(
                        titre="Mission Investissements d'avenir",
                        titre_court="Invest. avenir",
                    ),
                ),
                (103433, MissionRef(titre="Mission Justice", titre_court="Justice")),
                (
                    103434,
                    MissionRef(
                        titre="Mission Médias, livre et industries culturelles",
                        titre_court="Médias, livre",
                    ),
                ),
                (103435, MissionRef(titre="Mission Outre-mer", titre_court="")),
                (
                    103436,
                    MissionRef(
                        titre="Mission Pouvoirs publics", titre_court="Pouv. pub."
                    ),
                ),
                (
                    103437,
                    MissionRef(
                        titre="Mission Recherche et enseignement supérieur",
                        titre_court="Rech. et ens. sup.",
                    ),
                ),
                (
                    103438,
                    MissionRef(
                        titre="Mission Régimes sociaux et de retraite",
                        titre_court="Régimes soc.",
                    ),
                ),
                (
                    103439,
                    MissionRef(
                        titre="Mission Relations avec les collectivités territoriales",
                        titre_court="Relations C.T.",
                    ),
                ),
                (
                    103440,
                    MissionRef(
                        titre="Mission Remboursements et dégrèvements",
                        titre_court="Remboursements",
                    ),
                ),
                (103441, MissionRef(titre="Mission Santé", titre_court="Santé")),
                (103442, MissionRef(titre="Mission Sécurités", titre_court="Sécu.")),
                (
                    103443,
                    MissionRef(
                        titre="Mission Solidarité, insertion et égalité des chances",
                        titre_court="Solidarité",
                    ),
                ),
                (
                    103444,
                    MissionRef(
                        titre="Mission Sport, jeunesse et vie associative",
                        titre_court="Sport jeun. asso.",
                    ),
                ),
                (
                    103445,
                    MissionRef(
                        titre="Mission Travail et emploi", titre_court="Trav. emploi"
                    ),
                ),
                # Budgets annexes.
                (
                    103395,
                    MissionRef(
                        titre="Budget annexe - Contrôle et exploitation aériens",
                        titre_court="Contrôle et exploitation aériens",
                    ),
                ),
                (
                    103396,
                    MissionRef(
                        titre="Budget annexe - Publications officielles et information administrative",  # noqa
                        titre_court="Publications officielles et information administrative",  # noqa
                    ),
                ),
                # Comptes spéciaux.
                (
                    103397,
                    MissionRef(
                        titre="Compte spécial - Accords monétaires internationaux",
                        titre_court="Accords monétaires internationaux",
                    ),
                ),
                (
                    103398,
                    MissionRef(
                        titre="Compte spécial - Aides à l'acquisition de véhicules propres",  # noqa
                        titre_court="Aides à l'acquisition de véhicules propres",
                    ),
                ),
                (
                    103399,
                    MissionRef(
                        titre="Compte spécial - Avances à divers services de l'État ou organismes gérant des services publics",  # noqa
                        titre_court="Avances à divers services de l'État ou organismes gérant des services publics",  # noqa
                    ),
                ),
                (
                    103400,
                    MissionRef(
                        titre="Compte spécial - Avances à l'audiovisuel public",
                        titre_court="Avances à l'audiovisuel public",
                    ),
                ),
                (
                    103401,
                    MissionRef(
                        titre="Compte spécial - Avances aux collectivités territoriales",  # noqa
                        titre_court="Avances aux collectivités territoriales",
                    ),
                ),
                (
                    103402,
                    MissionRef(
                        titre="Compte spécial - Contrôle de la circulation et du stationnement routiers",  # noqa
                        titre_court="Contrôle de la circulation et du stationnement routiers",  # noqa
                    ),
                ),
                (
                    103403,
                    MissionRef(
                        titre="Compte spécial - Développement agricole et rural",
                        titre_court="Développement agricole et rural",
                    ),
                ),
                (
                    103404,
                    MissionRef(
                        titre="Compte spécial - Financement des aides aux collectivités pour l'électrification rurale",  # noqa
                        titre_court="Financement des aides aux collectivités pour l'électrification rurale",  # noqa
                    ),
                ),
                (
                    103405,
                    MissionRef(
                        titre="Compte spécial - Financement national du développement et de la modernisation de l'apprentissage",  # noqa
                        titre_court="Financement national du développement et de la modernisation de l'apprentissage",  # noqa
                    ),
                ),
                (
                    103406,
                    MissionRef(
                        titre="Compte spécial - Gestion du patrimoine immobilier de l'État",  # noqa
                        titre_court="Gestion du patrimoine immobilier de l'État",
                    ),
                ),
                (
                    103407,
                    MissionRef(
                        titre="Compte spécial - Participation de la France au désendettement de la Grèce",  # noqa
                        titre_court="Participation de la France au désendettement de la Grèce",  # noqa
                    ),
                ),
                (
                    103408,
                    MissionRef(
                        titre="Compte spécial - Participations financières de l'État",
                        titre_court="Participations financières de l'État",
                    ),
                ),
                (
                    103409,
                    MissionRef(
                        titre="Compte spécial - Pensions", titre_court="Pensions"
                    ),
                ),
                (
                    103410,
                    MissionRef(
                        titre="Compte spécial - Prêts à des États étrangers",
                        titre_court="Prêts à des États étrangers",
                    ),
                ),
                (
                    103411,
                    MissionRef(
                        titre="Compte spécial - Prêts et avances à des particuliers ou à des organismes privés",  # noqa
                        titre_court="Prêts et avances à des particuliers ou à des organismes privés",  # noqa
                    ),
                ),
                (
                    103412,
                    MissionRef(
                        titre="Compte spécial - Services nationaux de transport conventionnés de voyageurs",  # noqa
                        titre_court="Services nationaux de transport conventionnés de voyageurs",  # noqa
                    ),
                ),
                (
                    103413,
                    MissionRef(
                        titre="Compte spécial - Transition énergétique",
                        titre_court="Transition énergétique",
                    ),
                ),
                # Articles non rattachés.
                (103394, MissionRef(titre="", titre_court="")),
            ],
        }
    },
}
