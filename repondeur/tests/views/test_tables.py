import transaction


def test_tables_empty(app, lecture_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david)

    email = user_david.email
    resp = app.get(f"/lectures/an.15.269.PO717460/tables/{email}", user=email)

    assert resp.status_code == 200
    assert "Ma table" in resp.text


def test_tables_with_amendement(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(amendements_an[0])
        DBSession.add(user_david)
        table = user_david.table_for(lecture_an)
        table.amendements.append(amendements_an[0])

    email = user_david.email
    resp = app.get(f"/lectures/an.15.269.PO717460/tables/{email}", user=email)

    assert resp.status_code == 200
    assert "Ma table" in resp.text
    assert f'Nº&nbsp;<span class="numero">{amendements_an[0]}</span>' in resp.text
    assert f'Nº&nbsp;<span class="numero">{amendements_an[1]}</span>' not in resp.text


def test_tables_can_release_amendement(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(amendements_an[0])
        DBSession.add(user_david)
        table = user_david.table_for(lecture_an)
        table.amendements.append(amendements_an[0])

    email = user_david.email
    resp = app.get(f"/lectures/an.15.269.PO717460/tables/{email}", user=email)
    assert f'Nº&nbsp;<span class="numero">{amendements_an[0]}</span>' in resp.text

    form = resp.forms["release-amendement"]
    assert list(form.fields.keys()) == ["nums", "target", "submit"]
    resp = form.submit()
    assert resp.status_code == 302
    assert (
        resp.location
        == "https://zam.test/lectures/an.15.269.PO717460/tables/david@example.com"
    )

    resp = app.get(resp.location, user=email)
    assert f'Nº&nbsp;<span class="numero">{amendements_an[0]}</span>' not in resp.text


def test_tables_can_transfer_amendement(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(amendements_an[0])
        DBSession.add(user_david)
        table = user_david.table_for(lecture_an)
        table.amendements.append(amendements_an[0])

    email = user_david.email
    resp = app.get(f"/lectures/an.15.269.PO717460/tables/{email}", user=email)
    assert (
        f'<a href="https://zam.test/lectures/an.15.269.PO717460/transfer_amendements'
        f'?nums={amendements_an[0]}" class="button primary">Transférer</a>'
    ) in resp.text


def test_tables_grab_amendement(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        DBSession.add(user_david)
        table = user_david.table_for(lecture_an)
        assert len(table.amendements) == 0

    email = user_david.email
    resp = app.post(
        f"/lectures/an.15.269.PO717460/tables/{email}",
        {"nums": [amendements_an[0].num]},
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

    with transaction.manager:
        DBSession.add(user_david)
        table = user_david.table_for(lecture_an)
        assert len(table.amendements) == 0

    email = user_david.email
    resp = app.post(
        f"/lectures/an.15.269.PO717460/tables/{email}",
        {"nums": [amendements_an[0].num, amendements_an[1].num]},
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


def test_tables_release_amendement(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession, Amendement, User

    with transaction.manager:
        DBSession.add(user_david)
        table = user_david.table_for(lecture_an)
        table.amendements.append(amendements_an[0])
        assert len(user_david.table_for(lecture_an).amendements) == 1

    email = user_david.email
    resp = app.post(
        f"/lectures/an.15.269.PO717460/tables/{email}",
        {"nums": [amendements_an[0].num]},
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


def test_tables_release_amendements(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession, Amendement, User

    with transaction.manager:
        DBSession.add(user_david)
        table = user_david.table_for(lecture_an)
        table.amendements.append(amendements_an[0])
        table.amendements.append(amendements_an[1])
        assert len(user_david.table_for(lecture_an).amendements) == 2

    email = user_david.email
    resp = app.post(
        f"/lectures/an.15.269.PO717460/tables/{email}",
        {"nums": [amendements_an[0].num, amendements_an[1].num]},
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


def test_tables_transfer_amendement(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        DBSession.add_all([user_david, user_ronan])
        table_david = user_david.table_for(lecture_an)
        table_david.amendements.append(amendements_an[0])
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
        "<abbr title='david@example.com'>David</abbr> "
        "a transféré l’amendement à « Ronan (ronan@example.com) »"
    )


def test_tables_transfer_amendements(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        DBSession.add_all([user_david, user_ronan])
        table_david = user_david.table_for(lecture_an)
        table_david.amendements.append(amendements_an[0])
        table_david.amendements.append(amendements_an[1])
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
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        DBSession.add_all([user_david, user_ronan])
        table_david = user_david.table_for(lecture_an)
        table_david.amendements.append(amendements_an[0])
        assert len(user_david.table_for(lecture_an).amendements) == 1
        assert len(user_ronan.table_for(lecture_an).amendements) == 0

    email = user_ronan.email
    resp = app.post(
        f"/lectures/an.15.269.PO717460/tables/{email}",
        {"nums": [amendements_an[0].num], "target": user_ronan.email},
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
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        DBSession.add_all([user_david, user_ronan])
        table_david = user_david.table_for(lecture_an)
        table_david.amendements.append(amendements_an[0])
        table_david.amendements.append(amendements_an[1])
        assert len(user_david.table_for(lecture_an).amendements) == 2
        assert len(user_ronan.table_for(lecture_an).amendements) == 0

    email = user_ronan.email
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
