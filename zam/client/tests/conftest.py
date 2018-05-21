import pytest
from selectolax.parser import HTMLParser

from decorators import require_env_vars
from loaders import load_source
from models import load_data
from utils import build_output_filename, render_and_save_html


@pytest.fixture(scope='module')
@require_env_vars(env_vars=['ZAM_INPUT', 'ZAM_OUTPUT'])
def document(*args: list) -> HTMLParser:
    """Read and parse the HTML output, generated if inexistent."""
    output_filename = build_output_filename()
    if not output_filename.exists():
        print('Generating the output file (approx. 50 sec)')
        title, items = load_source()
        articles, amendements, reponses = load_data(items)
        render_and_save_html(title, articles, amendements, reponses)
    with open(output_filename) as output:
        yield HTMLParser(output.read())
