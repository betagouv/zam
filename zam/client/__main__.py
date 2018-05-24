import sys

from logbook import StreamHandler
from minicli import cli, run

from loaders import load_source
from models import load_data
from templates import render_and_save_html

StreamHandler(sys.stdout).push_application()


@cli
def generate(limit: int=None) -> None:
    """Generate the final confidential page from sensitive sources.

    :limit: Number of articles to parse, useful for debugging (default=all).
    """
    title, items = load_source()
    articles, amendements, reponses = load_data(items, limit)
    render_and_save_html(title, articles, amendements, reponses)


run()
