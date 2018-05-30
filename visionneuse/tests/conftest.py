import pytest
from selectolax.parser import HTMLParser

from zam_visionneuse.__main__ import generate
from zam_visionneuse.decorators import require_env_vars


@pytest.fixture(scope="module")
@require_env_vars(
    env_vars=["ZAM_DRUPAL_SOURCE", "ZAM_ASPIRATEUR_SOURCE", "ZAM_OUTPUT"]
)
def output() -> HTMLParser:
    yield HTMLParser(generate())
