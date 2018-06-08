from pathlib import Path

import pytest
from selectolax.parser import HTMLParser

from zam_visionneuse.utils import build_output_filename


@pytest.fixture(scope="module")
def output() -> HTMLParser:
    output_file = Path.cwd().parent.parent / "output"  # TODO: find a better way!
    with open(build_output_filename(output_file)) as output:
        yield HTMLParser(output.read())
