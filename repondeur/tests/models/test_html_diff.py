from zam_repondeur.models.events.helpers import html_diff


def test_one_changed_word():
    assert html_diff("foo", "bar") == "<del>foo</del> <ins>bar</ins>"


def test_two_changed_words():
    assert html_diff("foo foo", "bar bar") == "<del>foo foo</del> <ins>bar bar</ins>"


def test_one_word_between_two_unchanged():
    assert (
        html_diff("foo bar foo", "foo baz foo")
        == "foo <del>bar</del> <ins>baz</ins> foo"
    )


def test_two_words_between_two_unchanged():
    assert (
        html_diff("foo bar bar foo", "foo baz baz foo")
        == "foo <del>bar bar</del> <ins>baz baz</ins> foo"
    )
