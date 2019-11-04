import transaction


def test_lecture_progress_status(app, lecture_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(lecture_an)
        lecture_an.set_fetch_progress(42, 100)

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/progress_status/",
        user=user_david,
    )

    assert resp.status_code == 200
    assert resp.content_type == "application/json"
    assert resp.json == {"current": 42, "total": 100}


def test_lecture_no_progress_status(app, lecture_an, user_david):
    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/progress_status/",
        user=user_david,
    )

    assert resp.status_code == 200
    assert resp.content_type == "application/json"
    assert resp.json == {}
