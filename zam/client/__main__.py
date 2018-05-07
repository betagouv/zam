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
def generate(input_dir, limit: int=None):
    """Return HTML directly on stdout, redirect to target accordingly.

    :input_dir: Source folder containing sensitive documents.
    :limit: Number of articles to parse, useful for debugging (default=all).
    """
    input_dir = Path(input_dir)
    source = input_dir / 'JSON - fichier de sauvegarde' / 'AN2-2018.json'
    source = load_json(source)[0]  # Unique item.
    articles = enhance_articles(source['list'], input_dir, limit)
    html_output = render(title=source['libelle'], articles=articles)
    print(html_output)


run()
