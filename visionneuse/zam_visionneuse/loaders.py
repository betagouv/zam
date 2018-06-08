import json
from pathlib import Path
from typing import List, Tuple

from .decorators import check_existence
from .parsers import parse_docx


def load_json(source_path: str) -> dict:
    with open(source_path) as source:
        return json.loads(source.read())


def load_drupal_source(reponses_file: str) -> Tuple[str, List[dict]]:
    source = load_json(reponses_file)[0]  # Unique item.
    return source["libelle"], source["list"]


def load_articles_contents_source(articles_file: str) -> List[dict]:
    return load_json(articles_file)  # type: ignore


def load_aspirateur_source(aspirateur_file: str) -> Tuple[str, List[dict]]:
    source = load_json(aspirateur_file)[0]  # Unique item.
    return source["libelle"], source["list"]


@check_existence
def load_docx(source_path: Path) -> str:
    with open(source_path, "rb") as source:
        content = parse_docx(source)
    # Get rid of (not proper docx) headers.
    return "\n".join(part for part in content.split("\n")[9:])
