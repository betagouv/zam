from zam_visionneuse.utils import strip_styles


def test_strip_styles_without_styles():
    assert strip_styles("") == ""
    assert strip_styles("<p>foo</foo>") == "<p>foo</foo>"


def test_strip_styles_with_style():
    assert strip_styles('<p style="text-align:justify;">foo') == "<p>foo"
