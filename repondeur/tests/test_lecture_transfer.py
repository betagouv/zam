import transaction


def test_lecture_get_transfer_amendements(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_ronan)

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
    assert resp.forms["transfer-amendements"].fields["target"][0].options == [
        ("", True, ""),
        ("david@example.com", False, "Moi — david@example.com"),
        ("ronan@example.com", False, "Ronan (ronan@example.com)"),
    ]
    assert "transfer-amendements-custom" not in resp.forms


def test_lecture_get_transfer_amendements_from_index(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_ronan)

    resp = app.get(
        "/lectures/an.15.269.PO717460/transfer_amendements",
        {"nums": [amendements_an[0]], "from_index": 1},
        user=user_david.email,
    )
    assert resp.status_code == 200
    assert resp.forms["transfer-amendements"].method == "POST"
    assert list(resp.forms["transfer-amendements"].fields.keys()) == [
        "nums",
        "from_index",
        "target",
        "submit",
    ]
    assert resp.forms["transfer-amendements"].fields["nums"][0].value == "666"
    assert resp.forms["transfer-amendements"].fields["target"][0].options == [
        ("", True, ""),
        ("david@example.com", False, "Moi — david@example.com"),
        ("ronan@example.com", False, "Ronan (ronan@example.com)"),
    ]
    assert resp.forms["transfer-amendements"].fields["from_index"][0].value == "1"
    assert "transfer-amendements-custom" not in resp.forms


def test_lecture_get_transfer_amendements_from_me(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_ronan)
        DBSession.add(amendements_an[0])
        DBSession.add(user_david)
        table_david = user_david.table_for(lecture_an)
        table_david.amendements.append(amendements_an[0])

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
    assert resp.forms["transfer-amendements"].fields["target"][0].options == [
        ("", True, ""),
        ("ronan@example.com", False, "Ronan (ronan@example.com)"),
    ]
    assert resp.forms["transfer-amendements-custom"].method == "POST"
    assert list(resp.forms["transfer-amendements-custom"].fields.keys()) == [
        "nums",
        "submit-index",
    ]
    assert resp.forms["transfer-amendements-custom"].fields["nums"][0].value == "666"


def test_lecture_get_transfer_amendements_from_other(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_ronan)
        DBSession.add(amendements_an[0])
        table_ronan = user_ronan.table_for(lecture_an)
        table_ronan.amendements.append(amendements_an[0])

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
    assert resp.forms["transfer-amendements"].fields["target"][0].options == [
        ("", True, ""),
        ("david@example.com", False, "Moi — david@example.com"),
        ("ronan@example.com", False, "Ronan (ronan@example.com)"),
    ]
    assert resp.forms["transfer-amendements-custom"].method == "POST"
    assert list(resp.forms["transfer-amendements-custom"].fields.keys()) == [
        "nums",
        "submit-index",
    ]
    assert resp.forms["transfer-amendements-custom"].fields["nums"][0].value == "666"


def test_lecture_post_transfer_amendements_to_me(
    app, lecture_an, amendements_an, user_david
):
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
    form = resp.forms["transfer-amendements"]
    form["target"] = user_david.email
    resp = form.submit("submit")
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


def test_lecture_post_transfer_amendements_to_me_from_index(
    app, lecture_an, amendements_an, user_david
):
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
    form = resp.forms["transfer-amendements"]
    form["target"] = user_david.email
    resp = form.submit("submit")
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


def test_lecture_post_transfer_amendements_to_index(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models import DBSession, User, Amendement

    with transaction.manager:
        DBSession.add(user_david)
        DBSession.add(amendements_an[0])
        table_david = user_david.table_for(lecture_an)
        table_david.amendements.append(amendements_an[0])

    resp = app.get(
        "/lectures/an.15.269.PO717460/transfer_amendements",
        {"nums": [amendements_an[0]]},
        user=user_david.email,
    )
    resp = resp.forms["transfer-amendements-custom"].submit("submit-index")
    assert resp.status_code == 302
    assert (
        resp.location
        == f"https://zam.test/lectures/an.15.269.PO717460/tables/{user_david.email}"
    )
    user_david = DBSession.query(User).filter(User.email == user_david.email).first()
    table = user_david.table_for(lecture_an)
    assert len(table.amendements) == 0
    amendement = (
        DBSession.query(Amendement)
        .filter(Amendement.num == amendements_an[0].num)
        .first()
    )
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a remis l’amendement dans l’index"
    )


def test_lecture_post_transfer_amendements_to_index_from_index(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models import DBSession, User, Amendement

    with transaction.manager:
        DBSession.add(user_david)
        DBSession.add(amendements_an[0])
        table_david = user_david.table_for(lecture_an)
        table_david.amendements.append(amendements_an[0])

    resp = app.get(
        "/lectures/an.15.269.PO717460/transfer_amendements",
        {"nums": [amendements_an[0]], "from_index": 1},
        user=user_david.email,
    )
    resp = resp.forms["transfer-amendements-custom"].submit("submit-index")
    assert resp.status_code == 302
    assert resp.location == "https://zam.test/lectures/an.15.269.PO717460/amendements"
    user_david = DBSession.query(User).filter(User.email == user_david.email).first()
    table = user_david.table_for(lecture_an)
    assert len(table.amendements) == 0
    amendement = (
        DBSession.query(Amendement)
        .filter(Amendement.num == amendements_an[0].num)
        .first()
    )
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a remis l’amendement dans l’index"
    )


def test_lecture_post_transfer_amendements_to_other(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        DBSession.add(user_david)
        DBSession.add(user_ronan)
        DBSession.add(amendements_an[0])
        table_david = user_david.table_for(lecture_an)
        table_david.amendements.append(amendements_an[0])

    resp = app.get(
        "/lectures/an.15.269.PO717460/transfer_amendements",
        {"nums": [amendements_an[0]]},
        user=user_david.email,
    )
    form = resp.forms["transfer-amendements"]
    form["target"] = user_ronan.email
    resp = form.submit()
    assert resp.status_code == 302
    assert (
        resp.location
        == f"https://zam.test/lectures/an.15.269.PO717460/tables/{user_david.email}"
    )
    user_david = DBSession.query(User).filter(User.email == user_david.email).first()
    table_david = user_david.table_for(lecture_an)
    assert len(table_david.amendements) == 0
    user_ronan = DBSession.query(User).filter(User.email == user_ronan.email).first()
    table_ronan = user_ronan.table_for(lecture_an)
    assert len(table_ronan.amendements) == 1
    assert table_ronan.amendements[0].events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a transféré l’amendement à « Ronan (ronan@example.com) »"
    )


def test_lecture_post_transfer_amendements_to_other_from_index(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        DBSession.add(user_david)
        DBSession.add(user_ronan)
        DBSession.add(amendements_an[0])
        table_david = user_david.table_for(lecture_an)
        table_david.amendements.append(amendements_an[0])

    resp = app.get(
        "/lectures/an.15.269.PO717460/transfer_amendements",
        {"nums": [amendements_an[0]], "from_index": 1},
        user=user_david.email,
    )
    form = resp.forms["transfer-amendements"]
    form["target"] = user_ronan.email
    resp = form.submit()
    assert resp.status_code == 302
    assert resp.location == "https://zam.test/lectures/an.15.269.PO717460/amendements"
    user_david = DBSession.query(User).filter(User.email == user_david.email).first()
    table_david = user_david.table_for(lecture_an)
    assert len(table_david.amendements) == 0
    user_ronan = DBSession.query(User).filter(User.email == user_ronan.email).first()
    table_ronan = user_ronan.table_for(lecture_an)
    assert len(table_ronan.amendements) == 1
    assert table_ronan.amendements[0].events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a transféré l’amendement à « Ronan (ronan@example.com) »"
    )
