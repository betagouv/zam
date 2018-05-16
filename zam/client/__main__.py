import os
import sys
from pathlib import Path

from logbook import StreamHandler
from minicli import cli, run

from loaders import load_json
from models import Amendements, Articles, Reponses
from templates import render, write_html
from utils import build_output_filename

StreamHandler(sys.stdout).push_application()


@cli
def generate(input_dir: str, output_dir: str, limit: int=None) -> None:
    """Generate the final confidential page from sensitive sources.

    :input_dir: Source folder path containing sensitive documents.
    :output_dir: Target folder path to generate the page to.
    :limit: Number of articles to parse, useful for debugging (default=all).
    """
    input_path = Path(input_dir)
    json_source = input_path / 'JSON - fichier de sauvegarde' / 'AN2-2018.json'
    source = load_json(json_source)[0]  # Unique item.
    title = source['libelle']
    items = source['list']
    articles = Articles.load(items, limit)
    articles.load_jaunes(items, input_path, limit)
    amendements = Amendements.load(items, articles, limit)
    amendements.load_contents(input_path)
    reponses = Reponses.load(items, articles, amendements, limit)
    html = render(title=title, articles=articles, reponses=reponses)
    output_filename = build_output_filename(output_dir)
    write_html(html, output_filename)


run()
