import logging
from typing import NamedTuple, Optional


logger = logging.getLogger(__name__)


class Mission(NamedTuple):
    num: Optional[int]
    titre: str
    titre_court: str


# Special case for PLF 2019
# cf. http://www.senat.fr/ordre-du-jour/files/Calendrier_budgetaire_PLF2019.pdf
MISSIONS = {
    "2018-2019": {
        146: {
            1: [Mission(103393, titre="", titre_court="")],
            2: [
                # Missions classiques.
                Mission(
                    103414,
                    titre="Mission Action et transformation publiques",
                    titre_court="Action transfo.",
                ),
                Mission(
                    103415,
                    titre="Mission Action extérieure de l'État",
                    titre_court="Action ext.",
                ),
                Mission(
                    103416,
                    titre="Mission Administration générale et territoriale de l'État",
                    titre_court="Administration",
                ),
                Mission(
                    103417,
                    titre="Mission Agriculture, alimentation, forêt et affaires rurales",  # noqa
                    titre_court="Agri. alim.",
                ),
                Mission(
                    103418,
                    titre="Mission Aide publique au développement",
                    titre_court="APD",
                ),
                Mission(
                    103419,
                    titre="Mission Anciens combattants, mémoire et liens avec la nation",  # noqa
                    titre_court="Anciens combattants",
                ),
                Mission(
                    103420,
                    titre="Mission Cohésion des territoires",
                    titre_court="Cohésion terr.",
                ),
                Mission(
                    103421,
                    titre="Mission Conseil et contrôle de l'État",
                    titre_court="Conseil et contr.",
                ),
                Mission(
                    103422,
                    titre="Mission Crédits non répartis",
                    titre_court="Crédits NR",
                ),
                Mission(103423, titre="Mission Culture", titre_court="Culture"),
                Mission(103424, titre="Mission Défense", titre_court="Défense"),
                Mission(
                    103425,
                    titre="Mission Direction de l'action du Gouvernement",
                    titre_court="Action Gouv.",
                ),
                Mission(
                    103426,
                    titre="Mission Écologie, développement et mobilité durables",
                    titre_court="Écologie",
                ),
                Mission(103427, titre="Mission Économie", titre_court="Économie"),
                Mission(
                    103428,
                    titre="Mission Engagements financiers de l'État",
                    titre_court="Engagements",
                ),
                Mission(
                    103429,
                    titre="Mission Enseignement scolaire",
                    titre_court="Enseignement sco.",
                ),
                Mission(
                    103430,
                    titre="Mission Gestion des finances publiques et des ressources humaines",  # noqa
                    titre_court="Fi. pub. et RH",
                ),
                Mission(
                    103431,
                    titre="Mission Immigration, asile et intégration",
                    titre_court="Immigration",
                ),
                Mission(
                    103432,
                    titre="Mission Investissements d'avenir",
                    titre_court="Invest. avenir",
                ),
                Mission(103433, titre="Mission Justice", titre_court="Justice"),
                Mission(
                    103434,
                    titre="Mission Médias, livre et industries culturelles",
                    titre_court="Médias, livre",
                ),
                Mission(103435, titre="Mission Outre-mer", titre_court=""),
                Mission(
                    103436, titre="Mission Pouvoirs publics", titre_court="Pouv. pub."
                ),
                Mission(
                    103437,
                    titre="Mission Recherche et enseignement supérieur",
                    titre_court="Rech. et ens. sup.",
                ),
                Mission(
                    103438,
                    titre="Mission Régimes sociaux et de retraite",
                    titre_court="Régimes soc.",
                ),
                Mission(
                    103439,
                    titre="Mission Relations avec les collectivités territoriales",
                    titre_court="Relations C.T.",
                ),
                Mission(
                    103440,
                    titre="Mission Remboursements et dégrèvements",
                    titre_court="Remboursements",
                ),
                Mission(103441, titre="Mission Santé", titre_court="Santé"),
                Mission(103442, titre="Mission Sécurités", titre_court="Sécu."),
                Mission(
                    103443,
                    titre="Mission Solidarité, insertion et égalité des chances",
                    titre_court="Solidarité",
                ),
                Mission(
                    103444,
                    titre="Mission Sport, jeunesse et vie associative",
                    titre_court="Sport jeun. asso.",
                ),
                Mission(
                    103445,
                    titre="Mission Travail et emploi",
                    titre_court="Trav. emploi",
                ),
                # Budgets annexes.
                Mission(
                    103395,
                    titre="Budget annexe - Contrôle et exploitation aériens",
                    titre_court="Contrôle et exploitation aériens",
                ),
                Mission(
                    103396,
                    titre="Budget annexe - Publications officielles et information administrative",  # noqa
                    titre_court="Publications officielles et information administrative",  # noqa
                ),
                # Comptes spéciaux.
                Mission(
                    103397,
                    titre="Compte spécial - Accords monétaires internationaux",
                    titre_court="Accords monétaires internationaux",
                ),
                Mission(
                    103398,
                    titre="Compte spécial - Aides à l'acquisition de véhicules propres",
                    titre_court="Aides à l'acquisition de véhicules propres",
                ),
                Mission(
                    103399,
                    titre="Compte spécial - Avances à divers services de l'État ou organismes gérant des services publics",  # noqa
                    titre_court="Avances à divers services de l'État ou organismes gérant des services publics",  # noqa
                ),
                Mission(
                    103400,
                    titre="Compte spécial - Avances à l'audiovisuel public",
                    titre_court="Avances à l'audiovisuel public",
                ),
                Mission(
                    103401,
                    titre="Compte spécial - Avances aux collectivités territoriales",
                    titre_court="Avances aux collectivités territoriales",
                ),
                Mission(
                    103402,
                    titre="Compte spécial - Contrôle de la circulation et du stationnement routiers",  # noqa
                    titre_court="Contrôle de la circulation et du stationnement routiers",  # noqa
                ),
                Mission(
                    103403,
                    titre="Compte spécial - Développement agricole et rural",
                    titre_court="Développement agricole et rural",
                ),
                Mission(
                    103404,
                    titre="Compte spécial - Financement des aides aux collectivités pour l'électrification rurale",  # noqa
                    titre_court="Financement des aides aux collectivités pour l'électrification rurale",  # noqa
                ),
                Mission(
                    103405,
                    titre="Compte spécial - Financement national du développement et de la modernisation de l'apprentissage",  # noqa
                    titre_court="Financement national du développement et de la modernisation de l'apprentissage",  # noqa
                ),
                Mission(
                    103406,
                    titre="Compte spécial - Gestion du patrimoine immobilier de l'État",
                    titre_court="Gestion du patrimoine immobilier de l'État",
                ),
                Mission(
                    103407,
                    titre="Compte spécial - Participation de la France au désendettement de la Grèce",  # noqa
                    titre_court="Participation de la France au désendettement de la Grèce",  # noqa
                ),
                Mission(
                    103408,
                    titre="Compte spécial - Participations financières de l'État",
                    titre_court="Participations financières de l'État",
                ),
                Mission(
                    103409, titre="Compte spécial - Pensions", titre_court="Pensions"
                ),
                Mission(
                    103410,
                    titre="Compte spécial - Prêts à des États étrangers",
                    titre_court="Prêts à des États étrangers",
                ),
                Mission(
                    103411,
                    titre="Compte spécial - Prêts et avances à des particuliers ou à des organismes privés",  # noqa
                    titre_court="Prêts et avances à des particuliers ou à des organismes privés",  # noqa
                ),
                Mission(
                    103412,
                    titre="Compte spécial - Services nationaux de transport conventionnés de voyageurs",  # noqa
                    titre_court="Services nationaux de transport conventionnés de voyageurs",  # noqa
                ),
                Mission(
                    103413,
                    titre="Compte spécial - Transition énergétique",
                    titre_court="Transition énergétique",
                ),
                # Articles non rattachés.
                Mission(103394, titre="", titre_court=""),
            ],
        }
    }
}
