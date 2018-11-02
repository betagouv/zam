import transaction
from datetime import datetime


def test_article_check(app, lecture_an, amendements_an):
    resp = app.get(
        "http://localhost/lectures/an.15.269.PO717460/articles/article.1../check",
        {"since": amendements_an[1].modified_at_timestamp},
    )
    assert resp.status_code == 200
    assert resp.json == {
        "modified_amendements_numbers": [],
        "modified_at": amendements_an[1].modified_at_timestamp,
    }


def test_article_check_updates(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    initial_modified_at_timestamp = amendements_an[0].modified_at_timestamp
    resp = app.get(
        "http://localhost/lectures/an.15.269.PO717460/articles/article.1../check",
        {"since": initial_modified_at_timestamp},
    )
    assert resp.status_code == 200
    assert resp.json == {
        "modified_amendements_numbers": ["999"],
        "modified_at": amendements_an[1].modified_at_timestamp,
    }

    with transaction.manager:
        amendements_an[0].modified_at = datetime.utcnow()
        DBSession.add_all(amendements_an)

    resp2 = app.get(
        "http://localhost/lectures/an.15.269.PO717460/articles/article.1../check",
        {"since": initial_modified_at_timestamp},
    )
    assert resp2.status_code == 200
    assert resp2.json == {
        "modified_amendements_numbers": ["666", "999"],
        "modified_at": amendements_an[0].modified_at_timestamp,
    }


def test_article_check_not_found(app, lecture_an, amendements_an):
    resp = app.get(
        "http://localhost/lectures/an.16.269.PO717460/articles/article.1../check",
        {"since": amendements_an[1].modified_at_timestamp},
        expect_errors=True,
    )
    assert resp.status_code == 404
