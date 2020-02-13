from typing import Dict, Optional, Union

from inscriptis import get_text

from zam_repondeur.models import Amendement

# NB: dict key order is used for spreadsheet columns order (Python 3.6+)
FIELDS = {
    "article": "Num article",
    "article_titre": "Titre article",
    "num": "Num amdt",
    "rectif": "Rectif",
    "parent": "Parent (sous-amdt)",
    "auteur": "Auteur",
    "groupe": "Groupe",
    "gouvernemental": "Gouvernemental",
    "corps": "Corps amdt",
    "expose": "Exposé amdt",
    "first_identique_num": "Identique",
    "avis": "Avis du Gouvernement",
    "objet": "Objet amdt",
    "reponse": "Réponse",
    "comments": "Commentaires",
    "affectation_email": "Affectation (email)",
    "affectation_name": "Affectation (nom)",
    "affectation_box": "Affectation (boite)",
    "sort": "Sort",
}


COLUMN_NAME_TO_FIELD = {col: attr for attr, col in FIELDS.items()}


def column_name_to_field(column_name: str) -> Optional[str]:
    return COLUMN_NAME_TO_FIELD.get(column_name)


HEADERS = FIELDS.values()


HTML_FIELDS = ["corps", "expose", "objet", "reponse", "comments"]


def export_amendement_for_spreadsheet(amendement: Amendement) -> dict:
    data: Dict[str, Union[str, int, bool]] = {
        "article": amendement.article.format(),
        "article_titre": amendement.article.user_content.title or "",
        "num": amendement.num,
        "rectif": amendement.rectif or "",
        "parent": amendement.parent and amendement.parent.num_disp or "",
        "auteur": amendement.auteur or "",
        "groupe": amendement.groupe or "",
        "gouvernemental": "Oui" if amendement.gouvernemental else "Non",
        "corps": html_to_text(amendement.corps or ""),
        "expose": html_to_text(amendement.expose or ""),
        "first_identique_num": amendement.first_identique_num or "",
        "avis": amendement.user_content.avis or "",
        "objet": html_to_text(amendement.user_content.objet or ""),
        "reponse": html_to_text(amendement.user_content.reponse or ""),
        "comments": html_to_text(amendement.user_content.comments or ""),
        "affectation_email": (
            amendement.location.user_table
            and amendement.location.user_table.user.email
            or ""
        ),
        "affectation_name": (
            amendement.location.user_table
            and amendement.location.user_table.user.name
            or ""
        ),
        "affectation_box": (
            amendement.location.shared_table
            and amendement.location.shared_table.titre
            or ""
        ),
        "sort": amendement.sort or "",
    }
    return data


def html_to_text(html: str) -> str:
    text: str = get_text(html).strip()
    return text
