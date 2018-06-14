import os
from pathlib import Path

import pytest
from selectolax.parser import HTMLParser

from zam_visionneuse.utils import build_output_filename


@pytest.fixture(scope="module")
def output() -> HTMLParser:
    output_folder = Path(os.environ["OUTPUT"])
    yield HTMLParser(build_output_filename(output_folder).read_text())
