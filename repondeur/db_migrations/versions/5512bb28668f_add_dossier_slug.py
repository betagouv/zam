"""Add dossier slug

Revision ID: 5512bb28668f
Revises: 851d659d6eef
Create Date: 2019-07-09 09:38:20.740275

"""
from http import HTTPStatus
from io import BytesIO, TextIOWrapper
from json import load
from typing import Any, Dict, Generator, IO, List, Tuple
from zipfile import ZipFile

from alembic import op
from slugify import slugify as _slugify
import requests
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "5512bb28668f"
down_revision = "851d659d6eef"
branch_labels = None
depends_on = None


def get_dossiers_slugs(*legislatures: int) -> Dict[str, str]:
    all_dossiers: Dict[str, str] = {}
    for legislature in legislatures:
        dossiers = _get_dossiers_slugs(legislature)
        all_dossiers.update(dossiers)
    return all_dossiers


def _get_dossiers_slugs(legislature: int) -> Dict[str, str]:
    # As of June 20th, 2019 the Assemblée Nationale website updated the way
    # their opendata zip content is splitted, without changing old
    # legislatures. Hence we have to keep two ways to parse their content
    # forever. And ever.
    if legislature <= 14:
        data = list(fetch_dossiers_legislatifs_and_textes(legislature).values())[0]
        slugs = parse_slugs(data["export"]["dossiersLegislatifs"]["dossier"])
    else:
        data = fetch_dossiers_legislatifs_and_textes(legislature)
        dossiers_data: List[Dict[str, Any]] = [
            dict_
            for filename, dict_ in data.items()
            if filename.startswith("json/dossierParlementaire")
        ]
        slugs = parse_slugs(dossiers_data)
    return slugs


def fetch_dossiers_legislatifs_and_textes(legislature: int) -> dict:
    legislature_roman = roman(legislature)
    url = (
        f"http://data.assemblee-nationale.fr/static/openData/repository/"
        f"{legislature}/loi/dossiers_legislatifs/"
        f"Dossiers_Legislatifs_{legislature_roman}.json.zip"
    )
    return {
        filename: load(json_file)
        for filename, json_file in extract_from_remote_zip(url)
    }


def roman(n: int) -> str:
    if n == 15:
        return "XV"
    if n == 14:
        return "XIV"
    raise NotImplementedError


def extract_from_remote_zip(url: str) -> Generator[Tuple[str, IO[str]], None, None]:
    response = requests.get(url)

    if response.status_code not in (HTTPStatus.OK, HTTPStatus.NOT_MODIFIED):
        message = f"Unexpected status code {response.status_code} while fetching {url}"
        raise RuntimeError(message)

    content_type = response.headers["content-type"]
    if content_type != "application/zip":
        message = (
            f"Unexpected content type {content_type} while fetching {url} "
            "(expected application/zip)"
        )
        raise RuntimeError(message)

    yield from extract_from_zip(BytesIO(response.content))


def extract_from_zip(content: BytesIO) -> Generator[Tuple[str, IO[str]], None, None]:
    with ZipFile(content) as zip_file:
        for filename in zip_file.namelist():
            with zip_file.open(filename) as file_:
                yield (filename, TextIOWrapper(file_, encoding="utf-8"))


def parse_slugs(dossiers: list) -> Dict[str, str]:
    dossier_dicts = (
        item["dossierParlementaire"] for item in dossiers if isinstance(item, dict)
    )
    return {
        dossier_dict["uid"]: dossier_dict["titreDossier"]["titreChemin"]
        for dossier_dict in dossier_dicts
        if is_dossier(dossier_dict)
    }


def is_dossier(data: dict) -> bool:
    # Some records don't have a type field, so we have to rely on the UID as a fall-back
    return _has_dossier_type(data) or _has_dossier_uid(data)


def _has_dossier_type(data: dict) -> bool:
    return data.get("@xsi:type") == "DossierLegislatif_Type"


def _has_dossier_uid(data: dict) -> bool:
    uid: str = data["uid"]
    return uid.startswith("DLR")


def generate_unique_slug(connection, slugs, uid, titre):
    slug = base_slug = slugify(slugs.get(uid) or titre)
    counter = 1
    while True:
        if counter > 1:
            slug = f"{base_slug}-{counter}"
        result = connection.execute(
            sa.text("SELECT uid FROM dossiers WHERE slug = :slug ;"), slug=slug
        )
        if result.first() is None:
            break
        counter += 1
    return slug


STOPWORDS = [
    "a",
    "au",
    "aux",
    "d",
    "dans",
    "de",
    "des",
    "du",
    "en",
    "et",
    "l",
    "la",
    "le",
    "les",
    "par",
    "pour",
    "sur",
    "un",
    "une",
]


def slugify(text: str) -> str:
    return _slugify(text, stopwords=STOPWORDS)


def upgrade():
    print("Adding dossier slugs...")
    op.add_column("dossiers", sa.Column("slug", sa.Text()))
    connection = op.get_bind()
    slugs = get_dossiers_slugs(14, 15)
    rows = connection.execute("SELECT uid, titre FROM dossiers;")
    for uid, titre in rows:
        slug = generate_unique_slug(connection, slugs, uid, titre)
        connection.execute(
            sa.text("UPDATE dossiers SET slug = :slug WHERE uid = :uid ;"),
            slug=slug,
            uid=uid,
        )
    op.alter_column("dossiers", "slug", nullable=False)
    op.create_index("ix_dossiers__slug", "dossiers", ["slug"], unique=True)


def downgrade():
    op.drop_index("ix_dossiers__slug")
    op.drop_column("dossiers", "slug")
