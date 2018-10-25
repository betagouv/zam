import transaction
from datetime import datetime, timedelta


def test_article_check(app, lecture_an, amendements_an):
    resp = app.get(
        "http://localhost/lectures/an.15.269.PO717460/articles/article.1../check"
    )
    assert resp.status_code == 200
    assert "modified_at" in resp.json
    now = datetime.utcnow()
    inf = (now - datetime(1970, 1, 1) - timedelta(seconds=10)).total_seconds()
    sup = (now - datetime(1970, 1, 1) + timedelta(seconds=10)).total_seconds()
    assert inf < resp.json["modified_at"] < sup


def test_article_check_updates(app, lecture_an, amendements_an):
    resp = app.get(
        "http://localhost/lectures/an.15.269.PO717460/articles/article.1../check"
    )
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendements_an[0].modified_at = datetime.utcnow()
        DBSession.add_all(amendements_an)

    resp2 = app.get(
        "http://localhost/lectures/an.15.269.PO717460/articles/article.1../check"
    )
    assert resp.json["modified_at"] < resp2.json["modified_at"]


def test_article_check_not_found(app, lecture_an, amendements_an):
    resp = app.get(
        "http://localhost/lectures/an.16.269.PO717460/articles/article.1../check",
        expect_errors=True,
    )
    assert resp.status_code == 404
