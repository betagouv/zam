import sys
import argparse
from pathlib import Path
from typing import List, NewType, Optional, TextIO

from logbook import StreamHandler

from .loaders import (
    load_articles_contents_source,
    load_aspirateur_source,
    load_drupal_source,
)
from .models import load_data
from .templates import render_and_save_html

StreamHandler(sys.stdout).push_application()
SystemStatus = NewType("SystemStatus", int)  # status code for sys.exit()


def generate(
    aspirateur_file: TextIO,
    reponses_file: TextIO,
    jaunes_folder: Path,
    articles_file: TextIO,
    output_folder: Path,
) -> str:
    """Generate the final confidential page from available sources."""
    title, aspirateur_items = load_aspirateur_source(aspirateur_file)
    _, drupal_items = load_drupal_source(reponses_file)
    articles_contents = load_articles_contents_source(articles_file)
    articles, amendements, reponses = load_data(
        aspirateur_items, drupal_items, articles_contents, jaunes_folder
    )
    return render_and_save_html(title, articles, amendements, reponses, output_folder)


def main(argv: Optional[List[str]] = None) -> SystemStatus:
    args = parse_args(argv=argv)

    generate(
        aspirateur_file=args.file_aspirateur,
        reponses_file=args.file_reponses,
        jaunes_folder=args.folder_jaunes,
        articles_file=args.file_articles,
        output_folder=args.folder_output,
    )

    return SystemStatus(0)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file-aspirateur",
        required=True,
        type=argparse.FileType("r"),
        help=(
            "chemin vers le fichier JSON issu de l’aspirateur "
            "(p.ex. amendements_2017-2018_63.json)"
        ),
    )
    parser.add_argument(
        "--file-reponses",
        required=True,
        type=argparse.FileType("r"),
        help="chemin vers le fichier JSON issu de Drupal (p.ex. Sénat1-2018.json)",
    )
    parser.add_argument(
        "--folder-jaunes",
        required=True,
        type=Path,
        help="chemin vers les fichiers jaunes (p.ex. `Jeu de docs - PDF, word/Sénat1/`)",
    )
    parser.add_argument(
        "--file-articles",
        required=True,
        type=argparse.FileType("r"),
        help="chemin vers le fichier JSON issu de TLFP (p.ex. tlfp-output.json)",
    )
    parser.add_argument(
        "--folder-output",
        required=True,
        type=Path,
        help="chemin vers le dossier de destination de la visionneuse",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    sys.exit(main())
