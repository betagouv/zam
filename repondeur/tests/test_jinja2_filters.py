import transaction
import pytest

from zam_repondeur.views.jinja2_filters import paragriphy, render_diff


@pytest.mark.parametrize(
    "input,output",
    [("", "<p></p>"), ("foo", "<p>foo</p>"), ("<p>bar</p>", "<p>bar</p>")],
)
def test_paragriphy(input, output):
    assert paragriphy(input) == output


def test_render_diff(article1_an):
    from zam_repondeur.models import DBSession
    from zam_repondeur.events.base import Event
    from zam_repondeur.events.article import UpdateArticleTitle

    with transaction.manager:
        UpdateArticleTitle.create(request=None, article=article1_an, title="Foo")

    event = DBSession.query(Event).order_by(Event.created_at.desc()).first()
    assert (
        render_diff(event.data["old_value"], event.data["new_value"])
        == "<del>«  »</del> à <ins>« Foo »</ins>"
    )

    with transaction.manager:
        UpdateArticleTitle.create(request=None, article=article1_an, title="Bar")

    event = DBSession.query(Event).order_by(Event.created_at.desc()).first()
    assert (
        render_diff(event.data["old_value"], event.data["new_value"])
        == "<del>« Foo »</del> à <ins>« Bar »</ins>"
    )
