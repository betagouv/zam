def test_empty():
    from zam_repondeur.models.events.helpers import html_diff

    assert html_diff("", "") == ""


def test_no_change():
    from zam_repondeur.models.events.helpers import html_diff

    assert html_diff("foo", "foo") == "foo"


def test_addition_only():
    from zam_repondeur.models.events.helpers import html_diff

    assert html_diff("", "foo") == "<ins>foo</ins>"


def test_deletion_only():
    from zam_repondeur.models.events.helpers import html_diff

    assert html_diff("foo", "") == "<del>foo</del>"


def test_one_changed_word():
    from zam_repondeur.models.events.helpers import html_diff

    assert html_diff("foo", "bar") == "<del>foo</del> <ins>bar</ins>"


def test_two_changed_words():
    from zam_repondeur.models.events.helpers import html_diff

    assert html_diff("foo foo", "bar bar") == "<del>foo foo</del> <ins>bar bar</ins>"


def test_one_word_between_two_unchanged():
    from zam_repondeur.models.events.helpers import html_diff

    assert (
        html_diff("foo bar foo", "foo baz foo")
        == "foo <del>bar</del> <ins>baz</ins> foo"
    )


def test_two_words_between_two_unchanged():
    from zam_repondeur.models.events.helpers import html_diff

    assert (
        html_diff("foo bar bar foo", "foo baz baz foo")
        == "foo <del>bar bar</del> <ins>baz baz</ins> foo"
    )


def test_html_escaping():
    from zam_repondeur.models.events.helpers import html_diff

    assert (
        html_diff("foo", "<blink>bar</blink>")
        == "<del>foo</del> <ins>&lt;blink&gt;bar&lt;/blink&gt;</ins>"
    )
