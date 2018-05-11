import os
import sys
from datetime import datetime
from pathlib import Path

from logbook import StreamHandler
from minicli import cli, run

from enhancers import enhance_articles
from loaders import load_json
from templates import render

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
    articles = enhance_articles(source['list'], input_path, limit)
    html_output = render(title=source['libelle'], articles=articles)
    output_root_path = Path(output_dir)
    current_branch = os.popen('git symbolic-ref --short HEAD').read().strip()
    if current_branch == 'master':
        output_filename = output_root_path / 'index.html'
    else:
        now = datetime.utcnow()
        output_dir = f'{now.isoformat()[:len("YYYY-MM-DD")]}-{current_branch}'
        output_path = output_root_path / output_dir
        output_path.mkdir(exist_ok=True)
        output_filename = output_path / 'index.html'
    with open(output_filename, 'w') as output_file:
        output_file.write(html_output)


run()
