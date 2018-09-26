from datetime import datetime, timedelta


def test_lecture_check(app, lecture_an):
    resp = app.get("http://localhost/lectures/an.15.269.PO717460/check")
    assert resp.status_code == 200
    assert "modified_at" in resp.json
    now = datetime.utcnow()
    inf = (now - datetime(1970, 1, 1) - timedelta(seconds=10)).total_seconds()
    sup = (now - datetime(1970, 1, 1) + timedelta(seconds=10)).total_seconds()
    assert inf < resp.json["modified_at"] < sup


def test_lecture_check_not_found(app, lecture_an):
    resp = app.get(
        "http://localhost/lectures/an.16.269.PO717460/check", expect_errors=True
    )
    assert resp.status_code == 404
