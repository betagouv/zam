import sys

from logbook import StreamHandler

from .loaders import load_drupal_source, load_aspirateur_source
from .models import load_data
from .templates import render_and_save_html

StreamHandler(sys.stdout).push_application()


def generate() -> str:
    """Generate the final confidential page from available sources."""
    title, aspirateur_items = load_aspirateur_source()
    _, drupal_items = load_drupal_source()
    articles, amendements, reponses = load_data(aspirateur_items, drupal_items)
    return render_and_save_html(title, articles, amendements, reponses)


def main() -> None:
    generate()
