import pytest
from selectolax.parser import HTMLParser

from decorators import require_env_vars
from loaders import load_aspirateur_source, load_drupal_source
from models import load_data
from templates import render_and_save_html


@pytest.fixture(scope="module")
@require_env_vars(
    env_vars=["ZAM_DRUPAL_SOURCE", "ZAM_ASPIRATEUR_SOURCE", "ZAM_OUTPUT"]
)
def document() -> HTMLParser:
    """Read and parse the HTML output, generated if inexistent."""
    title, drupal_items = load_drupal_source()
    _, aspirateur_items = load_aspirateur_source()
    articles, amendements, reponses = load_data(drupal_items, aspirateur_items)
    html = render_and_save_html(title, articles, amendements, reponses)
    yield HTMLParser(html)
