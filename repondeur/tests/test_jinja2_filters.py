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
    from zam_repondeur.models import DBSession, ArticleUserContentRevision

    with transaction.manager:
        article1_an.user_content.title = "Foo"
        DBSession.add(article1_an)

    revision = (
        DBSession.query(ArticleUserContentRevision)
        .order_by(ArticleUserContentRevision.created_at.desc())
        .first()
    )
    assert render_diff(revision, "title") == "<del>«  »</del> à <ins>« Foo »</ins>"

    with transaction.manager:
        article1_an.user_content.title = "Bar"
        DBSession.add(article1_an)

    revision = (
        DBSession.query(ArticleUserContentRevision)
        .order_by(ArticleUserContentRevision.created_at.desc())
        .first()
    )
    assert render_diff(revision, "title") == "<del>« Foo »</del> à <ins>« Bar »</ins>"

    assert render_diff(revision, "presentation") == " "
