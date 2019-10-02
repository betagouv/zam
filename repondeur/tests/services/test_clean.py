import pytest


def test_whitespace_is_stripped():
    from zam_repondeur.services.clean import clean_html

    assert clean_html(" foo   ") == "foo"


@pytest.mark.parametrize("tag", ["b", "div", "p", "sup"])
def test_allowed_tags_are_preserved(tag):
    from zam_repondeur.services.clean import clean_html

    html = f"<{tag}>foo</{tag}>"
    assert clean_html(html) == f"<{tag}>foo</{tag}>"


def test_table_tags_are_preserved():
    from zam_repondeur.services.clean import clean_html

    html = "<table><tr><td>foo</td></tr></table>"
    assert clean_html(html) == "<table><tbody><tr><td>foo</td></tr></tbody></table>"


def test_table_colspan_attributes_are_preserved():
    from zam_repondeur.services.clean import clean_html

    html = '<table><tr><td colspan="2">foo</td></tr></table>'
    assert (
        clean_html(html)
        == '<table><tbody><tr><td colspan="2">foo</td></tr></tbody></table>'
    )


@pytest.mark.parametrize("tag", ["body"])
def test_not_allowed_tags_are_removed(tag):
    from zam_repondeur.services.clean import clean_html

    html = f"<{tag}>foo</{tag}>"
    assert clean_html(html) == "foo"


def test_style_attributes_are_removed():
    from zam_repondeur.services.clean import clean_html

    html = '<p style="text-align: justify">foo</p>'
    assert clean_html(html) == "<p>foo</p>"
