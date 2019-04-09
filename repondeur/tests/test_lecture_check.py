from datetime import datetime

import transaction


def test_lecture_check(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(lecture_an)
        initial_modified_at_timestamp = lecture_an.modified_amendements_at_timestamp

    resp = app.get(
        "/lectures/an.15.269.PO717460/check",
        {"since": initial_modified_at_timestamp},
        user=user_david,
    )
    assert resp.status_code == 200
    assert resp.json == {
        "modified_amendements_numbers": [],
        "modified_at": lecture_an.modified_amendements_at_timestamp,
    }


def test_lecture_check_updates(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add_all(amendements_an)
        initial_modified_at_timestamp = amendements_an[
            0
        ].lecture.modified_amendements_at_timestamp

    resp = app.get(
        "/lectures/an.15.269.PO717460/check",
        {"since": initial_modified_at_timestamp},
        user=user_david,
    )
    assert resp.status_code == 200
    assert resp.json == {
        "modified_amendements_numbers": [],
        "modified_at": initial_modified_at_timestamp,
    }

    with transaction.manager:
        amendements_an[0].modified_at = datetime.utcnow()
        DBSession.add_all(amendements_an)

    resp2 = app.get(
        "/lectures/an.15.269.PO717460/check",
        {"since": initial_modified_at_timestamp},
        user=user_david,
    )
    assert resp2.status_code == 200
    assert resp2.json == {
        "modified_amendements_numbers": ["666"],
        "modified_at": amendements_an[0].modified_at_timestamp,
    }

    with transaction.manager:
        amendements_an[0].article.modified_at = datetime.utcnow()
        DBSession.add_all(amendements_an)


def test_lecture_check_not_found(app, lecture_an, amendements_an, user_david):
    resp = app.get(
        "/lectures/an.16.269.PO717460/check",
        {"since": amendements_an[1].modified_at_timestamp},
        user=user_david,
        expect_errors=True,
    )
    assert resp.status_code == 404
