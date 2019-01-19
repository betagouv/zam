import pytest

from zam_repondeur.views.jinja2_filters import paragriphy


@pytest.mark.parametrize(
    "input,output",
    [("", "<p></p>"), ("foo", "<p>foo</p>"), ("<p>bar</p>", "<p>bar</p>")],
)
def test_paragriphy(input, output):
    assert paragriphy(input) == output
