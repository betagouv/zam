from zam_repondeur.models.events.helpers import text_to_html


def test_one_changed_word():
    assert text_to_html("foo", "bar") == "<del>foo</del> <ins>bar</ins>"


def test_two_changed_words():
    assert (
        text_to_html("foo foo", "bar bar")
        == "<del>foo foo</del> <ins>bar bar</ins>"
    )


def test_one_word_between_two_unchanged():
    assert (
        text_to_html("foo bar foo", "foo baz foo")
        == "foo <del>bar</del> <ins>baz</ins> foo"
    )


def test_two_words_between_two_unchanged():
    assert (
        text_to_html("foo bar bar foo", "foo baz baz foo")
        == "foo <del>bar bar</del> <ins>baz baz</ins> foo"
    )
