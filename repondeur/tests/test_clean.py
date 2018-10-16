import pytest

from zam_repondeur.clean import clean_html


def test_whitespace_is_stripped():
    assert clean_html(" foo   ") == "foo"


@pytest.mark.parametrize("tag", ["b", "div", "p", "sup"])
def test_allowed_tags_are_preserved(tag):
    html = f"<{tag}>foo</{tag}>"
    assert clean_html(html) == f"<{tag}>foo</{tag}>"


def test_table_tags_are_preserved():
    html = "<table><tr><td>foo</td></tr></table>"
    assert clean_html(html) == "<table><tbody><tr><td>foo</td></tr></tbody></table>"


@pytest.mark.parametrize("tag", ["body"])
def test_not_allowed_tags_are_removed(tag):
    html = f"<{tag}>foo</{tag}>"
    assert clean_html(html) == "foo"


def test_style_attributes_are_removed():
    html = '<p style="text-align: justify">foo</p>'
    assert clean_html(html) == "<p>foo</p>"
