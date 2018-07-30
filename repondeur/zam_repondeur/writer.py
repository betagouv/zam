import csv
import json
from contextlib import contextmanager
from dataclasses import fields
from itertools import groupby
from typing import Generator, Iterable, Tuple

import pdfkit
from inscriptis import get_text
from openpyxl import Workbook
from openpyxl.styles import Color, Font, PatternFill
from openpyxl.worksheet import Worksheet
from pyramid.request import Request
from pyramid_jinja2 import get_jinja2_environment
from xvfbwrapper import Xvfb

from .models import Amendement, Lecture


FIELDS_NAMES = {
    "article": "Nº article",
    "alinea": "Alinéa",
    "num": "Nº amdt",
    "auteur": "Auteur(s)",
    "date_depot": "Date de dépôt",
    "discussion_commune": "Discussion commune ?",
    "identique": "Identique ?",
    "parent_num": "Nº amdt parent",
    "parent_rectif": "Rectif parent",
    "objet": "Corps amdt",
    "resume": "Exposé amdt",
    "observations": "Objet amdt",
    "reponse": "Réponse",
    "comments": "Commentaires",
    "avis": "Avis du Gouvernement",
}


def rename_field(field_name: str) -> str:
    return FIELDS_NAMES.get(field_name, field_name.capitalize())


EXCLUDED_FIELDS = ["subdiv_contenu", "subdiv_jaune", "bookmarked_at"]
FIELDS = [
    field.name for field in fields(Amendement) if field.name not in EXCLUDED_FIELDS
]


HEADERS = [rename_field(field_name) for field_name in FIELDS]


DARK_BLUE = Color(rgb="00182848")
WHITE = Color(rgb="00FFFFFF")
GROUPS_COLORS = {
    # Sénat.
    "Les Républicains": "#2011e8",  # https://fr.wikipedia.org/wiki/Les_R%C3%A9publicains # noqa
    "UC": "#1e90ff",  # https://fr.wikipedia.org/wiki/Groupe_Union_centriste_(S%C3%A9nat) # noqa
    "SOCR": "#ff8080",  # https://fr.wikipedia.org/wiki/Groupe_socialiste_et_r%C3%A9publicain_(S%C3%A9nat) # noqa
    "RDSE": "#a38ebc",  # https://fr.wikipedia.org/wiki/Groupe_du_Rassemblement_d%C3%A9mocratique_et_social_europ%C3%A9en # noqa
    "Les Indépendants": "#30bfe9",  # https://fr.wikipedia.org/wiki/Groupe_Les_Ind%C3%A9pendants_%E2%80%93_R%C3%A9publique_et_territoires # noqa
    "NI": "#ffffff",  # https://fr.wikipedia.org/wiki/Non-inscrit
    "CRCE": "#dd0000",  # https://fr.wikipedia.org/wiki/Groupe_communiste,_r%C3%A9publicain,_citoyen_et_%C3%A9cologiste # noqa
    "LaREM": "#ffeb00",  # https://fr.wikipedia.org/wiki/Groupe_La_R%C3%A9publique_en_marche_(S%C3%A9nat) # noqa
    # AN.
    "La République en Marche": "#ffeb00",  # https://fr.wikipedia.org/wiki/Groupe_La_R%C3%A9publique_en_marche_(Assembl%C3%A9e_nationale) # noqa
    "Les Républicains": "#2011e8",  # https://fr.wikipedia.org/wiki/Groupe_Les_R%C3%A9publicains_(Assembl%C3%A9e_nationale) # noqa
    "Mouvement Démocrate et apparentés": "#ff8000",  # https://fr.wikipedia.org/wiki/Groupe_du_Mouvement_d%C3%A9mocrate_et_apparent%C3%A9s # noqa
    "Les Constructifs : républicains, UDI, indépendants": "#30bfe9",  # https://fr.wikipedia.org/wiki/Groupe_UDI,_Agir_et_ind%C3%A9pendants # noqa
    "Nouvelle Gauche": "#ff8080",  # https://fr.wikipedia.org/wiki/Groupe_socialiste_(Assembl%C3%A9e_nationale) # noqa
    "La France insoumise": "#cc2443",  # https://fr.wikipedia.org/wiki/Groupe_La_France_insoumise # noqa
    "Gauche démocrate et républicaine": "#dd0000",  # https://fr.wikipedia.org/wiki/Groupe_de_la_Gauche_d%C3%A9mocrate_et_r%C3%A9publicaine # noqa
    "Non inscrit": "#ffffff",  # https://fr.wikipedia.org/wiki/Non-inscrit
}


def write_csv(
    lecture: Lecture, amendements: Iterable[Amendement], filename: str, request: Request
) -> int:
    nb_rows = 0
    with open(filename, "w", encoding="utf-8") as file_:
        file_.write(";".join(HEADERS) + "\n")
        writer = csv.DictWriter(
            file_, fieldnames=FIELDS, delimiter=";", quoting=csv.QUOTE_MINIMAL
        )
        for amendement in amendements:
            writer.writerow(export_amendement(amendement))
            nb_rows += 1
    return nb_rows


@contextmanager
def xvfb_if_supported() -> Generator:
    try:
        with Xvfb():
            yield
    except (EnvironmentError, OSError, RuntimeError):
        yield


def write_pdf(
    lecture: Lecture, amendements: Iterable[Amendement], filename: str, request: Request
) -> int:
    from zam_repondeur.models.visionneuse import build_tree  # NOQA: circular

    amendements = list(amendements)
    articles = build_tree(amendements)
    env = get_jinja2_environment(request, name=".html")
    template = env.get_template("print.html")
    content = template.render(
        dossier_legislatif=lecture.dossier_legislatif,
        lecture=str(lecture),
        articles=articles,
    )
    options = {
        "quiet": "",
        "footer-center": f"{lecture.dossier_legislatif} • Page [page] sur [topage]",
    }
    with xvfb_if_supported():
        pdfkit.from_string(content, filename, options=options)
    return len(amendements)


def write_xlsx(
    lecture: Lecture, amendements: Iterable[Amendement], filename: str, request: Request
) -> int:
    wb = Workbook()
    ws = wb.active
    ws.title = "Amendements"

    _write_header_row(ws)
    nb_rows = _write_data_rows(ws, amendements)
    wb.save(filename)
    return nb_rows


def _write_header_row(ws: Worksheet) -> None:
    for column, value in enumerate(HEADERS, 1):
        cell = ws.cell(row=1, column=column)
        cell.value = value
        cell.fill = PatternFill(patternType="solid", fgColor=DARK_BLUE)
        cell.font = Font(color=WHITE, sz=8)


def _write_data_rows(ws: Worksheet, amendements: Iterable[Amendement]) -> int:
    nb_rows = 0
    for amend in amendements:
        values = tuple(export_amendement(amend).values())
        for column, value in enumerate(values, 1):
            cell = ws.cell(row=nb_rows + 2, column=column)
            cell.value = value
            cell.font = Font(sz=8)
        nb_rows += 1
    return nb_rows


def write_json_for_viewer(
    id_projet: int, title: str, amendements: Iterable[Amendement], filename: str
) -> int:
    data = _format_amendements(id_projet, title, amendements)
    with open(filename, "w") as file_:
        json.dump(data, file_)
    return len(list(amendements))


def _format_amendements(
    id_projet: int, title: str, amendements: Iterable[Amendement]
) -> list:
    def key_func(amendement: Amendement) -> Tuple[str, str, str, str]:
        return (
            amendement.subdiv_type,
            amendement.subdiv_num,
            amendement.subdiv_mult,
            amendement.subdiv_pos,
        )

    sorted_amendements = sorted(amendements, key=key_func)
    return [
        {
            "idProjet": id_projet,
            "libelle": title,
            "list": [
                _format_article(num, mult, pos, items)
                for (type_, num, mult, pos), items in groupby(
                    sorted_amendements, key=key_func
                )
                if type_ == "article"
            ],
        }
    ]


def _format_article(
    num: str, mult: str, pos: str, amendements: Iterable[Amendement]
) -> dict:
    return {
        "id": int(num),
        "pk": f"article-{num}{mult}{pos[:2]}",
        "multiplicatif": mult,
        "etat": pos[:2],
        "titre": "TODO",
        "jaune": f"jaune-{num}{mult}{pos[:2]}.pdf",
        "document": f"article-{num}{mult}{pos[:2]}.pdf",
        "amendements": [_format_amendement(amendement) for amendement in amendements],
    }


def _format_amendement(amendement: Amendement) -> dict:
    return {
        "id": amendement.num,
        "rectif": amendement.rectif or "",
        "pk": f"{amendement.num:06}",
        "etat": amendement.sort or "",
        "gouvernemental": amendement.gouvernemental,
        "auteur": amendement.auteur,
        "groupe": {
            "libelle": amendement.groupe or "",
            "couleur": GROUPS_COLORS.get(amendement.groupe, "#ffffff"),
        },
        "document": f"{amendement.num:06}-00.pdf",
        "dispositif": amendement.dispositif,
        "objet": amendement.objet,
        "resume": amendement.resume or "",
        "parent_num": amendement.parent_num or "",
        "parent_rectif": amendement.parent_rectif or "",
    }


HTML_FIELDS = ["objet", "dispositif", "observations", "reponse", "comments"]


def export_amendement(amendement: Amendement) -> dict:
    data: dict = amendement.asdict()
    for field_name in HTML_FIELDS:
        if data[field_name] is not None:
            data[field_name] = html_to_text(data[field_name])
    for excluded_field in EXCLUDED_FIELDS:
        if excluded_field in data.keys():
            del data[excluded_field]
    return data


def html_to_text(html: str) -> str:
    text: str = get_text(html).strip()
    return text
