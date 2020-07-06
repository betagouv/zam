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
def user_ronan(user_ronan, team_zam):
    """
    Override fixture so that we commit the user to the database
    """
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_ronan)
        user_ronan.teams.append(team_zam)

    return user_ronan


def test_lecture_get_transfer_amendements(app, lecture_an, amendements_an, user_david):
    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendements_an[0]]},
        user=user_david,
    )

    assert resp.status_code == 200
    assert (
        "Cet amendement est sur l’index"
        in resp.parser.css_first(".amendements li").text()
    )
    assert "checked" in resp.parser.css_first(".amendements li input").attributes

    form = resp.forms["transfer-amendements"]
    assert form.method == "POST"
    assert list(form.fields.keys()) == ["n", "target", "submit-to"]
    assert form.fields["n"][0].value == "666"
    assert form.fields["target"][0].options == [
        ("", True, ""),
        ("david@exemple.gouv.fr", False, "David (david@exemple.gouv.fr)"),
    ]


def test_lecture_get_transfer_amendements_with_shared_table(
    app, lecture_an, amendements_an, user_david, user_ronan, shared_table_lecture_an
):
    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendements_an[0]]},
        user=user_david,
    )

    assert resp.status_code == 200
    assert (
        "Cet amendement est sur l’index"
        in resp.parser.css_first(".amendements li").text()
    )
    assert "checked" in resp.parser.css_first(".amendements li input").attributes

    form = resp.forms["transfer-amendements"]
    assert form.method == "POST"
    assert list(form.fields.keys()) == ["n", "target", "submit-to"]
    assert form.fields["n"][0].value == "666"
    assert form.fields["target"][0].options == [
        ("", True, ""),
        ("david@exemple.gouv.fr", False, "David (david@exemple.gouv.fr)"),
        ("test-table", False, "Test table"),
        ("ronan@exemple.gouv.fr", False, "Ronan (ronan@exemple.gouv.fr)"),
    ]


def test_lecture_get_transfer_amendements_from_index(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendements_an[0]], "from_index": 1},
        user=user_david,
    )
    assert resp.status_code == 200

    form = resp.forms["transfer-amendements"]
    assert form.method == "POST"
    assert list(form.fields.keys()) == ["n", "from_index", "target", "submit-to"]
    assert form.fields["n"][0].value == "666"
    assert form.fields["target"][0].options == [
        ("", True, ""),
        ("david@exemple.gouv.fr", False, "David (david@exemple.gouv.fr)"),
        ("ronan@exemple.gouv.fr", False, "Ronan (ronan@exemple.gouv.fr)"),
    ]
    assert form.fields["from_index"][0].value == "1"


def test_lecture_get_transfer_amendements_from_me(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(amendements_an[0])
        table_david = user_david.table_for(lecture_an)
        table_david.add_amendement(amendements_an[0])

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendements_an[0]]},
        user=user_david,
    )
    assert resp.status_code == 200
    assert (
        "Cet amendement est sur votre table"
        in resp.parser.css_first(".amendements li").text()
    )
    assert "checked" in resp.parser.css_first(".amendements li input").attributes

    form = resp.forms["transfer-amendements"]
    assert form.method == "POST"
    assert list(form.fields.keys()) == ["n", "target", "submit-to", "submit-index"]
    assert form.fields["n"][0].value == "666"
    assert form.fields["target"][0].options == [
        ("", True, ""),
        ("ronan@exemple.gouv.fr", False, "Ronan (ronan@exemple.gouv.fr)"),
    ]


def test_lecture_get_transfer_amendements_from_shared_table(
    app, lecture_an, amendements_an, user_david, user_ronan, shared_table_lecture_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(amendements_an[0])
        amendements_an[0].location.shared_table = shared_table_lecture_an

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendements_an[0]]},
        user=user_david,
    )
    assert resp.status_code == 200
    assert (
        "Cet amendement est dans la boîte « Test table »"
        in resp.parser.css_first(".amendements li").text()
    )
    assert "checked" in resp.parser.css_first(".amendements li input").attributes

    form = resp.forms["transfer-amendements"]
    assert form.method == "POST"
    assert list(form.fields.keys()) == ["n", "target", "submit-to", "submit-index"]
    assert form.fields["n"][0].value == "666"
    assert form.fields["target"][0].options == [
        ("", True, ""),
        ("david@exemple.gouv.fr", False, "David (david@exemple.gouv.fr)"),
        ("ronan@exemple.gouv.fr", False, "Ronan (ronan@exemple.gouv.fr)"),
    ]


def test_lecture_get_transfer_amendements_including_me(
    app, lecture_an, amendements_an, user_david, user_ronan, user_david_table_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendements_an[0])

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": amendements_an},
        user=user_david,
    )
    assert resp.status_code == 200
    assert (
        "Cet amendement est sur votre table"
        in resp.parser.css_first(".amendements li").text()
    )
    assert "checked" in resp.parser.css_first(".amendements li input").attributes

    form = resp.forms["transfer-amendements"]
    assert form.method == "POST"
    assert list(form.fields.keys()) == ["n", "target", "submit-to", "submit-index"]
    assert form.fields["n"][0].value == "666"
    assert form.fields["target"][0].options == [
        ("", True, ""),
        ("david@exemple.gouv.fr", False, "David (david@exemple.gouv.fr)"),
        ("ronan@exemple.gouv.fr", False, "Ronan (ronan@exemple.gouv.fr)"),
    ]


def test_lecture_get_transfer_amendements_from_me_from_save(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(amendements_an[0])
        table_david = user_david.table_for(lecture_an)
        table_david.add_amendement(amendements_an[0])

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendements_an[0]], "from_save": 1},
        user=user_david,
    )
    assert resp.status_code == 200
    assert "Transférer l’amendement Nº 666" == " ".join(
        resp.parser.css_first("h1").text().split()
    )
    assert not resp.parser.css_first(".amendements")
    assert resp.parser.css_first('input[type="hidden"]').attributes["value"] == "666"

    form = resp.forms["transfer-amendements"]
    assert form.method == "POST"
    assert list(form.fields.keys()) == ["n", "target", "submit-to", "submit-index"]
    assert form.fields["n"][0].value == "666"
    assert form.fields["target"][0].options == [
        ("", True, ""),
        ("ronan@exemple.gouv.fr", False, "Ronan (ronan@exemple.gouv.fr)"),
    ]


def test_lecture_get_transfer_amendements_from_other(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(amendements_an[0])
        table_ronan = user_ronan.table_for(lecture_an)
        table_ronan.add_amendement(amendements_an[0])

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendements_an[0]]},
        user=user_david,
    )
    assert resp.status_code == 200
    assert (
        "Ronan (ronan@exemple.gouv.fr)"
        in resp.parser.css_first(".amendements li").text()
    )
    assert "checked" in resp.parser.css_first(".amendements li input").attributes
    assert (
        resp.parser.css_first(".amendements li nobr").attributes.get("class")
        == "user inactive"
    )

    form = resp.forms["transfer-amendements"]
    assert form.method == "POST"
    assert list(form.fields.keys()) == ["n", "target", "submit-to", "submit-index"]
    assert form.fields["n"][0].value == "666"
    assert form.fields["target"][0].options == [
        ("", True, ""),
        ("david@exemple.gouv.fr", False, "David (david@exemple.gouv.fr)"),
        ("ronan@exemple.gouv.fr", False, "Ronan (ronan@exemple.gouv.fr)"),
    ]


def test_lecture_get_transfer_amendements_from_other_active(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(amendements_an[0])
        table_ronan = user_ronan.table_for(lecture_an)
        table_ronan.add_amendement(amendements_an[0])
        user_ronan.record_activity()

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendements_an[0]]},
        user=user_david,
    )
    assert resp.status_code == 200
    assert (
        "Ronan (ronan@exemple.gouv.fr)"
        in resp.parser.css_first(".amendements li").text()
    )
    assert "checked" in resp.parser.css_first(".amendements li input").attributes
    assert (
        resp.parser.css_first(".amendements li nobr").attributes.get("class")
        == "user active"
    )


def test_lecture_get_transfer_amendements_from_edited_amendement(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(amendements_an[0])
        table_ronan = user_ronan.table_for(lecture_an)
        table_ronan.add_amendement(amendements_an[0])
        amendements_an[0].start_editing()

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendements_an[0]]},
        user=user_david,
    )
    assert resp.status_code == 200
    assert (
        "Ronan (ronan@exemple.gouv.fr)"
        in resp.parser.css_first(".amendements li").text()
    )
    assert "checked" not in resp.parser.css_first(".amendements li input").attributes
    assert (
        resp.parser.css_first(".amendements li nobr").attributes.get("class")
        == "user inactive"
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
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amdt]},
        user=user_david,
    )
    form = resp.forms["transfer-amendements"]
    form["target"] = user_david.email
    resp = form.submit("submit-to")

    # We're redirected to our table
    assert resp.status_code == 302
    assert resp.location == (
        (
            "https://zam.test/"
            "dossiers/plfss-2018/"
            "lectures/an.15.269.PO717460/"
            "tables/david@exemple.gouv.fr/"
        )
    )

    # Reload amendement as it was updated in another transaction
    amendement = Amendement.get(lecture_an, amendements_an[0].num)

    # The amendement is now on our table
    assert amendement.location.user_table.user.email == user_david.email
    assert amendement.location.shared_table is None
    assert amendement.table_name == "David"

    # An event was added to the amendement
    assert len(amendement.events) == 1
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a mis l’amendement sur sa table."
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
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendement]},
        user=user_david,
    )
    form = resp.forms["transfer-amendements"]
    form["target"] = user_david.email
    resp = form.submit("submit-to")

    # We're redirected to our table
    assert resp.status_code == 302
    assert resp.location == (
        (
            "https://zam.test/"
            "dossiers/plfss-2018/"
            "lectures/an.15.269.PO717460/"
            "tables/david@exemple.gouv.fr/"
        )
    )

    # Reload amendement as it was updated in another transaction
    amendement = Amendement.get(lecture_an, amendements_an[0].num)

    # The amendement is now on our table
    assert amendement.location.user_table.user.email == user_david.email

    # An event was added to the amendement
    assert len(amendement.events) == 1
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a mis l’amendement sur sa table."
    )


def test_lecture_post_transfer_amendements_to_index(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        DBSession.add(amendements_an[0])
        table_david = user_david.table_for(lecture_an)
        table_david.add_amendement(amendements_an[0])

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendements_an[0]]},
        user=user_david,
    )
    resp = resp.forms["transfer-amendements"].submit("submit-index")

    # We're redirected to our table
    assert resp.status_code == 302
    assert resp.location == (
        (
            "https://zam.test/"
            "dossiers/plfss-2018/"
            "lectures/an.15.269.PO717460/"
            "tables/david@exemple.gouv.fr/"
        )
    )

    # Reload amendement as it was updated in another transaction
    amendement = Amendement.get(lecture_an, amendements_an[0].num)

    # The amendement is now on the index
    assert amendement.location.user_table is None
    assert amendement.location.shared_table is None
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a remis l’amendement dans l’index."
    )
    assert amendement.table_name == ""


def test_lecture_post_transfer_amendements_to_index_from_index(
    app, lecture_an, lecture_an_url, amendements_an, user_david
):
    from zam_repondeur.models import Amendement, DBSession, User

    with transaction.manager:
        DBSession.add(amendements_an[0])
        table_david = user_david.table_for(lecture_an)
        table_david.add_amendement(amendements_an[0])

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendements_an[0]], "from_index": 1},
        user=user_david,
    )
    resp = resp.forms["transfer-amendements"].submit("submit-index")
    assert resp.status_code == 302
    assert resp.location == f"https://zam.test{lecture_an_url}/amendements/"
    user_david = DBSession.query(User).filter(User.email == user_david.email).first()
    table = user_david.table_for(lecture_an)
    assert len(table.amendements) == 0
    amendement = (
        DBSession.query(Amendement)
        .filter(Amendement.num == amendements_an[0].num)
        .first()
    )
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a remis l’amendement dans l’index."
    )


def test_lecture_post_transfer_amendements_to_other(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        DBSession.add(amendements_an[0])
        table_david = user_david.table_for(lecture_an)
        table_david.add_amendement(amendements_an[0])

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendements_an[0]]},
        user=user_david,
    )
    form = resp.forms["transfer-amendements"]
    form["target"] = user_ronan.email
    resp = form.submit()
    assert resp.status_code == 302
    assert resp.location == (
        (
            "https://zam.test/"
            "dossiers/plfss-2018/"
            "lectures/an.15.269.PO717460/"
            "tables/david@exemple.gouv.fr/"
        )
    )
    user_david = DBSession.query(User).filter(User.email == user_david.email).first()
    table_david = user_david.table_for(lecture_an)
    assert len(table_david.amendements) == 0
    user_ronan = DBSession.query(User).filter(User.email == user_ronan.email).first()
    table_ronan = user_ronan.table_for(lecture_an)
    assert len(table_ronan.amendements) == 1
    assert table_ronan.amendements[0].events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a transféré l’amendement à « Ronan (ronan@exemple.gouv.fr) »."
    )


def test_lecture_post_transfer_amendements_to_other_from_index(
    app, lecture_an, lecture_an_url, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        DBSession.add(amendements_an[0])
        table_david = user_david.table_for(lecture_an)
        table_david.add_amendement(amendements_an[0])

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendements_an[0]], "from_index": 1},
        user=user_david,
    )
    form = resp.forms["transfer-amendements"]
    form["target"] = user_ronan.email
    resp = form.submit()
    assert resp.status_code == 302
    assert resp.location == f"https://zam.test{lecture_an_url}/amendements/"
    user_david = DBSession.query(User).filter(User.email == user_david.email).first()
    table_david = user_david.table_for(lecture_an)
    assert len(table_david.amendements) == 0
    user_ronan = DBSession.query(User).filter(User.email == user_ronan.email).first()
    table_ronan = user_ronan.table_for(lecture_an)
    assert len(table_ronan.amendements) == 1
    assert table_ronan.amendements[0].events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a transféré l’amendement à « Ronan (ronan@exemple.gouv.fr) »."
    )


def test_lecture_post_transfer_amendements_from_void_to_shared_table(
    app, lecture_an, amendements_an, user_david, shared_table_lecture_an
):
    from zam_repondeur.models import Amendement

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendements_an[0]]},
        user=user_david,
    )
    form = resp.forms["transfer-amendements"]
    form["target"] = shared_table_lecture_an.slug
    resp = form.submit("submit-to")

    # We're redirected to our table
    assert resp.status_code == 302
    assert resp.location == (
        (
            "https://zam.test/"
            "dossiers/plfss-2018/"
            "lectures/an.15.269.PO717460/"
            "tables/david@exemple.gouv.fr/"
        )
    )

    # Reload amendement as it was updated in another transaction
    amendement = Amendement.get(lecture_an, amendements_an[0].num)

    # The amendement is now on the shared table.
    assert amendement.location.user_table is None
    assert amendement.location.shared_table.pk == shared_table_lecture_an.pk
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a transféré l’amendement à « Test table »."
    )
    assert amendement.table_name == "Test table"


def test_lecture_post_transfer_amendements_from_me_to_shared_table(
    app, lecture_an, amendements_an, user_david, shared_table_lecture_an
):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        DBSession.add(amendements_an[0])
        table_david = user_david.table_for(lecture_an)
        table_david.add_amendement(amendements_an[0])

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendements_an[0]]},
        user=user_david,
    )
    form = resp.forms["transfer-amendements"]
    form["target"] = shared_table_lecture_an.slug
    resp = form.submit("submit-to")

    # We're redirected to our table
    assert resp.status_code == 302
    assert resp.location == (
        (
            "https://zam.test/"
            "dossiers/plfss-2018/"
            "lectures/an.15.269.PO717460/"
            "tables/david@exemple.gouv.fr/"
        )
    )

    # Reload amendement as it was updated in another transaction
    amendement = Amendement.get(lecture_an, amendements_an[0].num)

    # The amendement is now on the shared table.
    assert amendement.location.user_table is None
    assert amendement.location.shared_table.pk == shared_table_lecture_an.pk
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a transféré l’amendement à « Test table »."
    )


def test_lecture_post_transfer_amendements_from_other_to_shared_table(
    app, lecture_an, amendements_an, user_david, user_ronan, shared_table_lecture_an
):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        DBSession.add(amendements_an[0])
        table_ronan = user_ronan.table_for(lecture_an)
        table_ronan.add_amendement(amendements_an[0])

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendements_an[0]]},
        user=user_david,
    )
    form = resp.forms["transfer-amendements"]
    form["target"] = shared_table_lecture_an.slug
    resp = form.submit("submit-to")

    # We're redirected to our table
    assert resp.status_code == 302
    assert resp.location == (
        (
            "https://zam.test/"
            "dossiers/plfss-2018/"
            "lectures/an.15.269.PO717460/"
            "tables/david@exemple.gouv.fr/"
        )
    )

    # Reload amendement as it was updated in another transaction
    amendement = Amendement.get(lecture_an, amendements_an[0].num)

    # The amendement is now on the shared table.
    assert amendement.location.user_table is None
    assert amendement.location.shared_table.pk == shared_table_lecture_an.pk
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a transféré l’amendement de « Ronan (ronan@exemple.gouv.fr) » "
        "à « Test table »."
    )


def test_lecture_post_transfer_amendements_from_shared_table_to_void(
    app, lecture_an, amendements_an, user_david, shared_table_lecture_an
):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        DBSession.add(amendements_an[0])
        amendements_an[0].location.shared_table = shared_table_lecture_an

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendements_an[0]]},
        user=user_david,
    )
    resp = resp.forms["transfer-amendements"].submit("submit-index")

    # We're redirected to our table
    assert resp.status_code == 302
    assert resp.location == (
        (
            "https://zam.test/"
            "dossiers/plfss-2018/"
            "lectures/an.15.269.PO717460/"
            "tables/david@exemple.gouv.fr/"
        )
    )

    # Reload amendement as it was updated in another transaction
    amendement = Amendement.get(lecture_an, amendements_an[0].num)

    # The amendement is now on the index.
    assert amendement.location.user_table is None
    assert amendement.location.shared_table is None
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a remis l’amendement de « Test table » dans l’index."
    )


def test_lecture_post_transfer_amendements_from_shared_table_to_me(
    app, lecture_an, amendements_an, user_david, shared_table_lecture_an
):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        DBSession.add(amendements_an[0])
        amendements_an[0].location.shared_table = shared_table_lecture_an

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendements_an[0]]},
        user=user_david,
    )
    form = resp.forms["transfer-amendements"]
    form["target"] = user_david.email
    resp = form.submit("submit-to")

    # We're redirected to our table
    assert resp.status_code == 302
    assert resp.location == (
        (
            "https://zam.test/"
            "dossiers/plfss-2018/"
            "lectures/an.15.269.PO717460/"
            "tables/david@exemple.gouv.fr/"
        )
    )

    # Reload amendement as it was updated in another transaction
    amendement = Amendement.get(lecture_an, amendements_an[0].num)

    # The amendement is now on our table.
    assert amendement.location.user_table.user.email == user_david.email
    assert amendement.location.shared_table is None
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a transféré l’amendement de « Test table » à lui/elle-même."
    )


def test_lecture_post_transfer_amendements_from_shared_table_to_other(
    app, lecture_an, amendements_an, user_david, user_ronan, shared_table_lecture_an
):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        DBSession.add(amendements_an[0])
        amendements_an[0].location.shared_table = shared_table_lecture_an

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendements_an[0]]},
        user=user_david,
    )
    form = resp.forms["transfer-amendements"]
    form["target"] = user_ronan.email
    resp = form.submit("submit-to")

    # We're redirected to our table
    assert resp.status_code == 302
    assert resp.location == (
        (
            "https://zam.test/"
            "dossiers/plfss-2018/"
            "lectures/an.15.269.PO717460/"
            "tables/david@exemple.gouv.fr/"
        )
    )

    # Reload amendement as it was updated in another transaction
    amendement = Amendement.get(lecture_an, amendements_an[0].num)

    # The amendement is now on their table.
    assert amendement.location.user_table.user.email == user_ronan.email
    assert amendement.location.shared_table is None
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a transféré l’amendement de « Test table » "
        "à « Ronan (ronan@exemple.gouv.fr) »."
    )


def test_lecture_post_transfer_amendements_from_void_to_noname_user(
    app, lecture_an, amendements_an, user_david, team_zam
):
    from zam_repondeur.models import Amendement, DBSession, User

    with transaction.manager:
        # We simulate an invited user that has never been connected.
        user_noname = User.create(email="noname@exemple.gouv.fr")
        user_noname.teams.append(team_zam)
        DBSession.add(user_noname)

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/transfer_amendements",
        {"n": [amendements_an[0]]},
        user=user_david,
    )
    form = resp.forms["transfer-amendements"]
    form["target"] = user_noname.email
    resp = form.submit("submit-to")

    # We're redirected to our table
    assert resp.status_code == 302
    assert resp.location == (
        (
            "https://zam.test/"
            "dossiers/plfss-2018/"
            "lectures/an.15.269.PO717460/"
            "tables/david@exemple.gouv.fr/"
        )
    )

    # Reload amendement as it was updated in another transaction
    amendement = Amendement.get(lecture_an, amendements_an[0].num)

    # The amendement is now on the noname user table.
    assert amendement.location.user_table.pk == user_noname.pk
    assert amendement.location.shared_table is None
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a transféré l’amendement à « noname@exemple.gouv.fr »."
    )
    assert amendement.table_name == "noname@exemple.gouv.fr"
