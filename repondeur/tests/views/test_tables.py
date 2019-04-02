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


def test_tables_empty(app, lecture_an, user_david):

    email = user_david.email
    resp = app.get(f"/lectures/an.15.269.PO717460/tables/{email}", user=email)

    assert resp.status_code == 200
    assert "Ma table" in resp.text


def test_tables_with_amendement(
    app, lecture_an, amendements_an, user_david, user_david_table_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendements_an[0])

    email = user_david.email
    resp = app.get(f"/lectures/an.15.269.PO717460/tables/{email}", user=email)

    assert resp.status_code == 200
    assert "Ma table" in resp.text
    assert f'Nº&nbsp;<span class="numero">{amendements_an[0]}</span>' in resp.text
    assert f'Nº&nbsp;<span class="numero">{amendements_an[1]}</span>' not in resp.text


def test_tables_grab_amendement(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession, User

    assert len(user_david.table_for(lecture_an).amendements) == 0

    email = user_david.email
    resp = app.post(
        f"/lectures/an.15.269.PO717460/tables/{email}",
        {"nums": [amendements_an[0].num], "submit-table": True},
        user=email,
    )
    assert resp.status_code == 302
    assert (
        resp.location == f"https://zam.test/lectures/an.15.269.PO717460/tables/{email}"
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


def test_tables_grab_amendements(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession, User

    assert len(user_david.table_for(lecture_an).amendements) == 0

    email = user_david.email
    resp = app.post(
        f"/lectures/an.15.269.PO717460/tables/{email}",
        {"nums": [amendements_an[0].num, amendements_an[1].num], "submit-table": True},
        user=email,
    )
    assert resp.status_code == 302
    assert (
        resp.location == f"https://zam.test/lectures/an.15.269.PO717460/tables/{email}"
    )
    user_david = DBSession.query(User).filter(User.email == user_david.email).first()
    table = user_david.table_for(lecture_an)
    assert len(table.amendements) == 2
    assert table.amendements[0].num == amendements_an[0].num
    assert table.amendements[0].lecture == amendements_an[0].lecture
    assert len(table.amendements[0].events) == 1
    assert table.amendements[0].events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a mis l’amendement sur sa table"
    )
    assert table.amendements[1].num == amendements_an[1].num
    assert table.amendements[1].lecture == amendements_an[1].lecture
    assert len(table.amendements[1].events) == 1
    assert table.amendements[1].events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a mis l’amendement sur sa table"
    )


def test_tables_release_amendement(
    app, lecture_an, amendements_an, user_david, user_david_table_an
):
    from zam_repondeur.models import DBSession, Amendement, User

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendements_an[0])

    assert len(user_david.table_for(lecture_an).amendements) == 1

    email = user_david.email
    resp = app.post(
        f"/lectures/an.15.269.PO717460/tables/{email}",
        {"nums": [amendements_an[0].num], "submit-index": True},
        user=email,
    )
    assert resp.status_code == 302
    assert (
        resp.location == f"https://zam.test/lectures/an.15.269.PO717460/tables/{email}"
    )
    user_david = DBSession.query(User).filter(User.email == user_david.email).first()
    table = user_david.table_for(lecture_an)
    assert len(table.amendements) == 0
    amendement = (
        DBSession.query(Amendement)
        .filter(Amendement.num == amendements_an[0].num)
        .first()
    )
    assert len(amendement.events) == 1
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a remis l’amendement dans l’index"
    )


def test_tables_release_amendements(
    app, lecture_an, amendements_an, user_david, user_david_table_an
):
    from zam_repondeur.models import DBSession, Amendement, User

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendements_an[0])
        user_david_table_an.amendements.append(amendements_an[1])

    assert len(user_david.table_for(lecture_an).amendements) == 2

    email = user_david.email
    resp = app.post(
        f"/lectures/an.15.269.PO717460/tables/{email}",
        {"nums": [amendements_an[0].num, amendements_an[1].num], "submit-index": True},
        user=email,
    )
    assert resp.status_code == 302
    assert (
        resp.location == f"https://zam.test/lectures/an.15.269.PO717460/tables/{email}"
    )
    user_david = DBSession.query(User).filter(User.email == user_david.email).first()
    table = user_david.table_for(lecture_an)
    assert len(table.amendements) == 0
    amendement = (
        DBSession.query(Amendement)
        .filter(Amendement.num == amendements_an[0].num)
        .first()
    )
    assert len(amendement.events) == 1
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a remis l’amendement dans l’index"
    )
    amendement = (
        DBSession.query(Amendement)
        .filter(Amendement.num == amendements_an[1].num)
        .first()
    )
    assert len(amendement.events) == 1
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a remis l’amendement dans l’index"
    )


class TestTransfer:
    def test_transfer_one_amendement_to_someone_else(
        self,
        app,
        lecture_an,
        amendements_an,
        user_david,
        user_david_table_an,
        user_ronan,
        user_ronan_table_an,
    ):
        from zam_repondeur.models import DBSession, User

        with transaction.manager:
            DBSession.add_all([user_david_table_an, user_ronan_table_an])
            user_david_table_an.amendements.append(amendements_an[0])

        assert len(user_david.table_for(lecture_an).amendements) == 1
        assert len(user_ronan.table_for(lecture_an).amendements) == 0

        email = user_david.email
        resp = app.post(
            f"/lectures/an.15.269.PO717460/tables/{email}",
            {"nums": [amendements_an[0].num], "target": user_ronan.email},
            user=email,
        )
        assert resp.status_code == 302
        assert (
            resp.location
            == f"https://zam.test/lectures/an.15.269.PO717460/tables/{email}"
        )
        user_david = (
            DBSession.query(User).filter(User.email == user_david.email).first()
        )
        table_david = user_david.table_for(lecture_an)
        user_ronan = (
            DBSession.query(User).filter(User.email == user_ronan.email).first()
        )
        table_ronan = user_ronan.table_for(lecture_an)
        assert len(table_david.amendements) == 0
        assert len(table_ronan.amendements) == 1
        assert table_ronan.amendements[0].num == amendements_an[0].num
        assert table_ronan.amendements[0].lecture == amendements_an[0].lecture
        assert len(table_ronan.amendements[0].events) == 1
        assert table_ronan.amendements[0].events[0].render_summary() == (
            "<abbr title='david@example.com'>David</abbr> "
            "a transféré l’amendement à « Ronan (ronan@example.com) »"
        )

    def test_transfer_one_amendement_to_myself_is_a_no_op(
        self, app, lecture_an, amendements_an, user_david, user_david_table_an
    ):
        from zam_repondeur.models import DBSession, User

        with transaction.manager:
            DBSession.add(user_david_table_an)
            user_david_table_an.amendements.append(amendements_an[0])

        assert len(user_david.table_for(lecture_an).amendements) == 1

        email = user_david.email
        resp = app.post(
            f"/lectures/an.15.269.PO717460/tables/{email}",
            {"nums": [amendements_an[0].num], "submit-table": True},
            user=email,
        )
        assert resp.status_code == 302
        assert (
            resp.location
            == f"https://zam.test/lectures/an.15.269.PO717460/tables/{email}"
        )
        user_david = (
            DBSession.query(User).filter(User.email == user_david.email).first()
        )
        table_david = user_david.table_for(lecture_an)
        assert len(table_david.amendements) == 1
        assert table_david.amendements[0].num == amendements_an[0].num
        assert table_david.amendements[0].lecture == amendements_an[0].lecture
        assert len(table_david.amendements[0].events) == 0

    def test_transfer_one_amendement_to_index_manually_is_forbidden(
        self, app, lecture_an, amendements_an, user_david, user_david_table_an
    ):
        from zam_repondeur.models import DBSession, User

        with transaction.manager:
            DBSession.add(user_david_table_an)
            user_david_table_an.amendements.append(amendements_an[0])

        assert len(user_david.table_for(lecture_an).amendements) == 1

        email = user_david.email
        resp = app.post(
            f"/lectures/an.15.269.PO717460/tables/{email}",
            {"nums": [amendements_an[0].num], "target": ""},
            user=email,
        )
        assert resp.status_code == 302
        assert resp.location == (
            "https://zam.test/lectures/an.15.269.PO717460/transfer_amendements?nums=666"
        )
        user_david = (
            DBSession.query(User).filter(User.email == user_david.email).first()
        )
        table_david = user_david.table_for(lecture_an)
        assert len(table_david.amendements) == 1
        assert table_david.amendements[0].num == amendements_an[0].num
        assert table_david.amendements[0].lecture == amendements_an[0].lecture
        assert len(table_david.amendements[0].events) == 0

    def test_transfer_multiple_amendements_to_someone_else(
        self,
        app,
        lecture_an,
        amendements_an,
        user_david,
        user_david_table_an,
        user_ronan,
    ):
        from zam_repondeur.models import DBSession, User

        with transaction.manager:
            DBSession.add(user_david_table_an)
            user_david_table_an.amendements.append(amendements_an[0])
            user_david_table_an.amendements.append(amendements_an[1])

        assert len(user_david.table_for(lecture_an).amendements) == 2
        assert len(user_ronan.table_for(lecture_an).amendements) == 0

        email = user_david.email
        resp = app.post(
            f"/lectures/an.15.269.PO717460/tables/{email}",
            {
                "nums": [amendements_an[0].num, amendements_an[1].num],
                "target": user_ronan.email,
            },
            user=email,
        )
        assert resp.status_code == 302
        assert (
            resp.location
            == f"https://zam.test/lectures/an.15.269.PO717460/tables/{email}"
        )
        user_david = (
            DBSession.query(User).filter(User.email == user_david.email).first()
        )
        table_david = user_david.table_for(lecture_an)
        user_ronan = (
            DBSession.query(User).filter(User.email == user_ronan.email).first()
        )
        table_ronan = user_ronan.table_for(lecture_an)
        assert len(table_david.amendements) == 0
        assert len(table_ronan.amendements) == 2
        assert table_ronan.amendements[0].num == amendements_an[0].num
        assert table_ronan.amendements[0].lecture == amendements_an[0].lecture
        assert len(table_ronan.amendements[0].events) == 1
        assert table_ronan.amendements[0].events[0].render_summary() == (
            "<abbr title='david@example.com'>David</abbr> "
            "a transféré l’amendement à « Ronan (ronan@example.com) »"
        )
        assert table_ronan.amendements[1].num == amendements_an[1].num
        assert table_ronan.amendements[1].lecture == amendements_an[1].lecture
        assert len(table_ronan.amendements[1].events) == 1
        assert table_ronan.amendements[1].events[0].render_summary() == (
            "<abbr title='david@example.com'>David</abbr> "
            "a transféré l’amendement à « Ronan (ronan@example.com) »"
        )


def test_tables_steal_amendement(
    app, lecture_an, amendements_an, user_david, user_david_table_an, user_ronan
):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendements_an[0])

    assert len(user_david.table_for(lecture_an).amendements) == 1
    assert len(user_ronan.table_for(lecture_an).amendements) == 0

    email = user_ronan.email
    resp = app.post(
        f"/lectures/an.15.269.PO717460/tables/{email}",
        {"nums": [amendements_an[0].num], "submit-table": True},
        user=email,
    )
    assert resp.status_code == 302
    assert (
        resp.location == f"https://zam.test/lectures/an.15.269.PO717460/tables/{email}"
    )
    user_david = DBSession.query(User).filter(User.email == user_david.email).first()
    table_david = user_david.table_for(lecture_an)
    user_ronan = DBSession.query(User).filter(User.email == user_ronan.email).first()
    table_ronan = user_ronan.table_for(lecture_an)
    assert len(table_david.amendements) == 0
    assert len(table_ronan.amendements) == 1
    assert table_ronan.amendements[0].num == amendements_an[0].num
    assert table_ronan.amendements[0].lecture == amendements_an[0].lecture
    assert len(table_ronan.amendements[0].events) == 1
    assert table_ronan.amendements[0].events[0].render_summary() == (
        "<abbr title='ronan@example.com'>Ronan</abbr> "
        "a transféré l’amendement de « David (david@example.com) » à lui/elle-même"
    )


def test_tables_steal_amendements(
    app, lecture_an, amendements_an, user_david, user_david_table_an, user_ronan
):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendements_an[0])
        user_david_table_an.amendements.append(amendements_an[1])

    assert len(user_david.table_for(lecture_an).amendements) == 2
    assert len(user_ronan.table_for(lecture_an).amendements) == 0

    email = user_ronan.email
    resp = app.post(
        f"/lectures/an.15.269.PO717460/tables/{email}",
        {"nums": [amendements_an[0].num, amendements_an[1].num], "submit-table": True},
        user=email,
    )
    assert resp.status_code == 302
    assert (
        resp.location == f"https://zam.test/lectures/an.15.269.PO717460/tables/{email}"
    )
    user_david = DBSession.query(User).filter(User.email == user_david.email).first()
    table_david = user_david.table_for(lecture_an)
    user_ronan = DBSession.query(User).filter(User.email == user_ronan.email).first()
    table_ronan = user_ronan.table_for(lecture_an)
    assert len(table_david.amendements) == 0
    assert len(table_ronan.amendements) == 2
    assert table_ronan.amendements[0].num == amendements_an[0].num
    assert table_ronan.amendements[0].lecture == amendements_an[0].lecture
    assert len(table_ronan.amendements[0].events) == 1
    assert table_ronan.amendements[0].events[0].render_summary() == (
        "<abbr title='ronan@example.com'>Ronan</abbr> "
        "a transféré l’amendement de « David (david@example.com) » à lui/elle-même"
    )
    assert table_ronan.amendements[1].num == amendements_an[1].num
    assert table_ronan.amendements[1].lecture == amendements_an[1].lecture
    assert len(table_ronan.amendements[1].events) == 1
    assert table_ronan.amendements[1].events[0].render_summary() == (
        "<abbr title='ronan@example.com'>Ronan</abbr> "
        "a transféré l’amendement de « David (david@example.com) » à lui/elle-même"
    )


@pytest.mark.parametrize(
    "current,updated",
    [["", {"updated": "666_999"}], ["666", {"updated": "666_999"}], ["666_999", {}]],
)
def test_tables_check_with_amendements(
    app, lecture_an, amendements_an, user_david, user_david_table_an, current, updated
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendements_an[0])
        user_david_table_an.amendements.append(amendements_an[1])

    email = user_david.email
    resp = app.get(
        f"/lectures/an.15.269.PO717460/tables/{email}/check",
        {"current": current},
        user=email,
    )
    assert resp.status_code == 200
    assert resp.json == updated


@pytest.mark.parametrize(
    "current,updated",
    [["", {}], ["666", {"updated": ""}], ["666_999", {"updated": ""}]],
)
def test_tables_check_without_amendements(
    app, lecture_an, amendements_an, user_david, current, updated
):
    email = user_david.email
    resp = app.get(
        f"/lectures/an.15.269.PO717460/tables/{email}/check",
        {"current": current},
        user=email,
    )
    assert resp.status_code == 200
    assert resp.json == updated
