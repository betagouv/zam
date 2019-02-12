import transaction


def test_lecture_get_transfer_amendements(app, lecture_an, amendements_an, user_david):
    resp = app.get(
        "/lectures/an.15.269.PO717460/transfer_amendements",
        {"nums": [amendements_an[0]]},
        user=user_david.email,
    )
    assert resp.status_code == 200
    assert resp.forms["transfer-amendements"].method == "POST"
    assert list(resp.forms["transfer-amendements"].fields.keys()) == [
        "nums",
        "target",
        "submit",
    ]
    assert resp.forms["transfer-amendements"].fields["nums"][0].value == "666"
    assert (
        resp.forms["transfer-amendements"].fields["target"][0].value
        == "david@example.com"
    )


def test_lecture_post_transfer_amendements(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        DBSession.add(user_david)
        table = user_david.table_for(lecture_an)
        assert len(table.amendements) == 0

    resp = app.get(
        "/lectures/an.15.269.PO717460/transfer_amendements",
        {"nums": [amendements_an[0]]},
        user=user_david.email,
    )
    resp = resp.forms["transfer-amendements"].submit()
    assert resp.status_code == 302
    assert (
        resp.location
        == f"https://zam.test/lectures/an.15.269.PO717460/tables/{user_david.email}"
    )
    user_david = DBSession.query(User).filter(User.email == user_david.email).first()
    table = user_david.table_for(lecture_an)
    assert len(table.amendements) == 1
    assert table.amendements[0].num == amendements_an[0].num
    assert table.amendements[0].lecture == amendements_an[0].lecture
    assert len(table.amendements[0].events) == 1
    assert table.amendements[0].events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a mis l’amendement sur sa table"
    )
