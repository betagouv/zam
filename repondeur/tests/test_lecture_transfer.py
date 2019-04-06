import pytest
import transaction


@pytest.fixture
def user_david(user_david):
    """
    Override fixture so that we commit the user to the database
    """
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david)

    return user_david


@pytest.fixture
def user_ronan(user_ronan):
    """
    Override fixture so that we commit the user to the database
    """
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_ronan)

    return user_ronan


def test_lecture_get_transfer_amendements(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    resp = app.get(
        "/lectures/an.15.269.PO717460/transfer_amendements",
        {"nums": [amendements_an[0]]},
        user=user_david.email,
    )

    assert resp.status_code == 200
    assert (
        "Cet amendement est sur l’index"
        in resp.parser.css_first(".amendements li").text()
    )
    assert "checked" in resp.parser.css_first(".amendements li input").attributes

    assert resp.form.method == "POST"
    assert list(resp.form.fields.keys()) == ["nums", "target", "submit"]
    assert resp.form.fields["nums"][0].value == "666"
    assert resp.form.fields["target"][0].options == [
        ("", True, ""),
        ("david@example.com", False, "Moi — David (david@example.com)"),
        ("ronan@example.com", False, "Ronan (ronan@example.com)"),
    ]


def test_lecture_get_transfer_amendements_from_index(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    resp = app.get(
        "/lectures/an.15.269.PO717460/transfer_amendements",
        {"nums": [amendements_an[0]], "from_index": 1},
        user=user_david.email,
    )
    assert resp.status_code == 200
    assert resp.form.method == "POST"
    assert list(resp.form.fields.keys()) == ["nums", "from_index", "target", "submit"]
    assert resp.form.fields["nums"][0].value == "666"
    assert resp.form.fields["target"][0].options == [
        ("", True, ""),
        ("david@example.com", False, "Moi — David (david@example.com)"),
        ("ronan@example.com", False, "Ronan (ronan@example.com)"),
    ]
    assert resp.form.fields["from_index"][0].value == "1"


def test_lecture_get_transfer_amendements_from_me(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(amendements_an[0])
        table_david = user_david.table_for(lecture_an)
        table_david.amendements.append(amendements_an[0])

    resp = app.get(
        "/lectures/an.15.269.PO717460/transfer_amendements",
        {"nums": [amendements_an[0]]},
        user=user_david.email,
    )
    assert resp.status_code == 200
    assert (
        "Cet amendement est sur votre table"
        in resp.parser.css_first(".amendements li").text()
    )
    assert "checked" in resp.parser.css_first(".amendements li input").attributes

    assert resp.form.method == "POST"
    assert list(resp.form.fields.keys()) == ["nums", "target", "submit", "submit-index"]
    assert resp.form.fields["nums"][0].value == "666"
    assert resp.form.fields["target"][0].options == [
        ("", True, ""),
        ("ronan@example.com", False, "Ronan (ronan@example.com)"),
    ]


def test_lecture_get_transfer_amendements_including_me(
    app, lecture_an, amendements_an, user_david, user_ronan, user_david_table_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendements_an[0])

    resp = app.get(
        "/lectures/an.15.269.PO717460/transfer_amendements",
        {"nums": amendements_an},
        user=user_david.email,
    )
    assert resp.status_code == 200
    assert (
        "Cet amendement est sur votre table"
        in resp.parser.css_first(".amendements li").text()
    )
    assert "checked" in resp.parser.css_first(".amendements li input").attributes

    assert resp.form.method == "POST"
    assert list(resp.form.fields.keys()) == ["nums", "target", "submit", "submit-index"]
    assert resp.form.fields["nums"][0].value == "666"
    assert resp.form.fields["target"][0].options == [
        ("", True, ""),
        ("david@example.com", False, "Moi — David (david@example.com)"),
        ("ronan@example.com", False, "Ronan (ronan@example.com)"),
    ]


def test_lecture_get_transfer_amendements_from_me_from_save(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(amendements_an[0])
        table_david = user_david.table_for(lecture_an)
        table_david.amendements.append(amendements_an[0])

    resp = app.get(
        "/lectures/an.15.269.PO717460/transfer_amendements",
        {"nums": [amendements_an[0]], "from_save": 1},
        user=user_david.email,
    )
    assert resp.status_code == 200
    assert "Transférer l’amendement Nº 666" == " ".join(
        resp.parser.css_first("h1").text().split()
    )
    assert not resp.parser.css_first(".amendements")
    assert resp.parser.css_first('input[type="hidden"]').attributes["value"] == "666"

    assert resp.form.method == "POST"
    assert list(resp.form.fields.keys()) == ["nums", "target", "submit", "submit-index"]
    assert resp.form.fields["nums"][0].value == "666"
    assert resp.form.fields["target"][0].options == [
        ("", True, ""),
        ("ronan@example.com", False, "Ronan (ronan@example.com)"),
    ]


def test_lecture_get_transfer_amendements_from_other(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(amendements_an[0])
        table_ronan = user_ronan.table_for(lecture_an)
        table_ronan.amendements.append(amendements_an[0])

    resp = app.get(
        "/lectures/an.15.269.PO717460/transfer_amendements",
        {"nums": [amendements_an[0]]},
        user=user_david.email,
    )
    assert resp.status_code == 200
    assert (
        "Ronan (ronan@example.com)" in resp.parser.css_first(".amendements li").text()
    )
    assert "checked" in resp.parser.css_first(".amendements li input").attributes
    assert (
        resp.parser.css_first(".amendements li nobr").attributes.get("class")
        == "user inactive"
    )

    assert resp.form.method == "POST"
    assert list(resp.form.fields.keys()) == ["nums", "target", "submit", "submit-index"]
    assert resp.form.fields["nums"][0].value == "666"
    assert resp.form.fields["target"][0].options == [
        ("", True, ""),
        ("david@example.com", False, "Moi — David (david@example.com)"),
        ("ronan@example.com", False, "Ronan (ronan@example.com)"),
    ]


def test_lecture_get_transfer_amendements_from_other_active(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(amendements_an[0])
        table_ronan = user_ronan.table_for(lecture_an)
        table_ronan.amendements.append(amendements_an[0])
        user_ronan.record_activity()

    resp = app.get(
        "/lectures/an.15.269.PO717460/transfer_amendements",
        {"nums": [amendements_an[0]]},
        user=user_david.email,
    )
    assert resp.status_code == 200
    assert (
        "Ronan (ronan@example.com)" in resp.parser.css_first(".amendements li").text()
    )
    assert "checked" not in resp.parser.css_first(".amendements li input").attributes
    assert (
        resp.parser.css_first(".amendements li nobr").attributes.get("class")
        == "user active"
    )


def test_lecture_post_transfer_amendements_to_me(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models import Amendement

    # Our table is empty
    table = user_david.table_for(lecture_an)
    assert len(table.amendements) == 0

    amdt = amendements_an[0]

    resp = app.get(
        "/lectures/an.15.269.PO717460/transfer_amendements",
        {"nums": [amdt]},
        user=user_david.email,
    )
    form = resp.form
    form["target"] = user_david.email
    resp = form.submit("submit")

    # We're redirected to our table
    assert resp.status_code == 302
    assert (
        resp.location
        == f"https://zam.test/lectures/an.15.269.PO717460/tables/{user_david.email}"
    )

    # Reload amendement as it was updated in another transaction
    amendement = Amendement.get(lecture_an, amendements_an[0].num)

    # The amendement is now on our table
    assert amendement.user_table.user.email == user_david.email

    # An event was added to the amendement
    assert len(amendement.events) == 1
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a mis l’amendement sur sa table"
    )


def test_lecture_post_transfer_amendements_to_me_from_index(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models import Amendement

    # Our table is empty
    table = user_david.table_for(lecture_an)
    assert len(table.amendements) == 0

    amendement = amendements_an[0]

    resp = app.get(
        "/lectures/an.15.269.PO717460/transfer_amendements",
        {"nums": [amendement]},
        user=user_david.email,
    )
    form = resp.form
    form["target"] = user_david.email
    resp = form.submit("submit")

    # We're redirected to our table
    assert resp.status_code == 302
    assert (
        resp.location
        == f"https://zam.test/lectures/an.15.269.PO717460/tables/{user_david.email}"
    )

    # Reload amendement as it was updated in another transaction
    amendement = Amendement.get(lecture_an, amendements_an[0].num)

    # The amendement is now on our table
    assert amendement.user_table.user.email == user_david.email

    # An event was added to the amendement
    assert len(amendement.events) == 1
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a mis l’amendement sur sa table"
    )


def test_lecture_post_transfer_amendements_to_index(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models import DBSession, Amendement

    with transaction.manager:
        DBSession.add(amendements_an[0])
        table_david = user_david.table_for(lecture_an)
        table_david.amendements.append(amendements_an[0])

    resp = app.get(
        "/lectures/an.15.269.PO717460/transfer_amendements",
        {"nums": [amendements_an[0]]},
        user=user_david.email,
    )
    resp = resp.form.submit("submit-index")

    # We're redirected to our table
    assert resp.status_code == 302
    assert (
        resp.location
        == f"https://zam.test/lectures/an.15.269.PO717460/tables/{user_david.email}"
    )

    # Reload amendement as it was updated in another transaction
    amendement = Amendement.get(lecture_an, amendements_an[0].num)

    # The amendement is now on the index
    assert amendement.user_table is None
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a remis l’amendement dans l’index"
    )


def test_lecture_post_transfer_amendements_to_index_from_index(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models import DBSession, User, Amendement

    with transaction.manager:
        DBSession.add(amendements_an[0])
        table_david = user_david.table_for(lecture_an)
        table_david.amendements.append(amendements_an[0])

    resp = app.get(
        "/lectures/an.15.269.PO717460/transfer_amendements",
        {"nums": [amendements_an[0]], "from_index": 1},
        user=user_david.email,
    )
    resp = resp.form.submit("submit-index")
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
        DBSession.add(amendements_an[0])
        table_david = user_david.table_for(lecture_an)
        table_david.amendements.append(amendements_an[0])

    resp = app.get(
        "/lectures/an.15.269.PO717460/transfer_amendements",
        {"nums": [amendements_an[0]]},
        user=user_david.email,
    )
    form = resp.form
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
        DBSession.add(amendements_an[0])
        table_david = user_david.table_for(lecture_an)
        table_david.amendements.append(amendements_an[0])

    resp = app.get(
        "/lectures/an.15.269.PO717460/transfer_amendements",
        {"nums": [amendements_an[0]], "from_index": 1},
        user=user_david.email,
    )
    form = resp.form
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
