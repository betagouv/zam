from utils import strip_styles, warnumerate


def test_strip_styles_without_styles():
    assert strip_styles("") == ""
    assert strip_styles("<p>foo</foo>") == "<p>foo</foo>"


def test_strip_styles_with_style():
    assert strip_styles('<p style="text-align:justify;">foo') == "<p>foo"


def test_warnumerate_return_complete_list():
    assert list(warnumerate(["foo", "bar"], limit=None)) == ["foo", "bar"]


def test_warnumerate_return_limited_list():
    assert list(warnumerate(["foo", "bar", "baz"], limit=2)) == ["foo", "bar"]
