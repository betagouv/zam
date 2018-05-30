import sys

from logbook import StreamHandler

from .loaders import load_drupal_source, load_aspirateur_source
from .models import load_data
from .templates import render_and_save_html

StreamHandler(sys.stdout).push_application()


def generate() -> str:
    """Generate the final confidential page from sensitive sources."""
    title, drupal_items = load_drupal_source()
    _, aspirateur_items = load_aspirateur_source()
    articles, amendements, reponses = load_data(drupal_items, aspirateur_items)
    return render_and_save_html(title, articles, amendements, reponses)
