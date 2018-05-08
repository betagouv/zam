import sys
from pathlib import Path

from logbook import StreamHandler
from minicli import cli, run

from enhancers import enhance_articles
from loaders import load_json
from templates import render

# Given that we use stdout for the output, we log on stderr.
StreamHandler(sys.stderr).push_application()


@cli
def generate(input_dir: str, limit: int=None) -> None:
    """Return HTML directly on stdout, redirect to target accordingly.

    :input_dir: Source folder path containing sensitive documents.
    :limit: Number of articles to parse, useful for debugging (default=all).
    """
    input_path = Path(input_dir)
    json_source = input_path / 'JSON - fichier de sauvegarde' / 'AN2-2018.json'
    source = load_json(json_source)[0]  # Unique item.
    articles = enhance_articles(source['list'], input_path, limit)
    html_output = render(title=source['libelle'], articles=articles)
    print(html_output)


run()
