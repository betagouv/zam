import json
from pathlib import Path
from typing import List, Tuple, TextIO

from .decorators import check_existence
from .parsers import parse_docx


def load_json(source_path: str) -> dict:
    with open(source_path) as source:
        return json.loads(source.read())


def load_drupal_source(reponses_file: TextIO) -> Tuple[str, List[dict]]:
    source = json.load(reponses_file)[0]  # Unique item.
    return source["libelle"], source["list"]


def load_articles_contents_source(articles_file: TextIO) -> List[dict]:
    return json.load(articles_file)


def load_aspirateur_source(aspirateur_file: TextIO) -> Tuple[str, List[dict]]:
    source = json.load(aspirateur_file)[0]  # Unique item.
    return source["libelle"], source["list"]


@check_existence
def load_docx(source_path: Path) -> str:
    with open(source_path, "rb") as source:
        content = parse_docx(source)
    # Get rid of (not proper docx) headers.
    return "\n".join(part for part in content.split("\n")[9:])
