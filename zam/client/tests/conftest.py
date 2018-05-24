import pytest
from selectolax.parser import HTMLParser

from decorators import require_env_vars
from loaders import load_drupal_source
from models import load_data
from templates import render_and_save_html
from utils import build_output_filename


@pytest.fixture(scope='module')
@require_env_vars(env_vars=['ZAM_DRUPAL_SOURCE', 'ZAM_OUTPUT'])
def document() -> HTMLParser:
    """Read and parse the HTML output, generated if inexistent."""
    output_filename = build_output_filename()
    if not output_filename.exists():
        print('Generating the output file (approx. 50 sec)')
        title, items = load_drupal_source()
        articles, amendements, reponses = load_data(items, items)
        render_and_save_html(title, articles, amendements, reponses)
    with open(output_filename) as output:
        yield HTMLParser(output.read())
