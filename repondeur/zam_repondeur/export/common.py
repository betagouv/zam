from inscriptis import get_text

from zam_repondeur.models import Amendement

EXCLUDED_FIELDS = [
    "Amendement",
    "pk",
    "article_pk",
    "lecture_pk",
    "parent_pk",
    "parent_rectif",
    "subdiv_type",
    "subdiv_titre",
    "subdiv_num",
    "subdiv_mult",
    "subdiv_pos",
    "created_at",
    "modified_at",
    "user_table_pk",
]


HTML_FIELDS = ["corps", "expose", "objet", "reponse", "comments"]


def export_amendement(amendement: Amendement, strip_html: bool = True) -> dict:
    data: dict = amendement.asdict()
    for field_name in HTML_FIELDS:
        if data[field_name] is not None and strip_html:
            data[field_name] = html_to_text(data[field_name])
    for excluded_field in EXCLUDED_FIELDS:
        if excluded_field in data.keys():
            del data[excluded_field]
    return data


def html_to_text(html: str) -> str:
    text: str = get_text(html).strip()
    return text
