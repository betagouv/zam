import transaction


def test_spaces_empty(app, lecture_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david)

    email = user_david.email
    resp = app.get(f"/lectures/an.15.269.PO717460/spaces/{email}", user=email)

    assert resp.status_code == 200
    assert f"Table de David ({email})" in resp.text


def test_spaces_with_amendement(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david)
        user_david.space.amendements.append(amendements_an[0])

    email = user_david.email
    resp = app.get(f"/lectures/an.15.269.PO717460/spaces/{email}", user=email)

    assert resp.status_code == 200
    assert f"Table de David ({email})" in resp.text
    assert f"Nº&nbsp;<strong>{amendements_an[0]}</strong>" in resp.text
    assert f"Nº&nbsp;<strong>{amendements_an[1]}</strong>" not in resp.text


def test_spaces_grab_amendement(app, amendements_an, user_david):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        DBSession.add(user_david)
        assert len(user_david.space.amendements) == 0

    email = user_david.email
    resp = app.post(
        f"/lectures/an.15.269.PO717460/spaces/{email}",
        {"num": amendements_an[0].num},
        user=email,
    )
    assert resp.status_code == 302
    assert (
        resp.location == f"https://zam.test/lectures/an.15.269.PO717460/spaces/{email}"
    )
    user_david = DBSession.query(User).filter(User.email == user_david.email).first()
    assert len(user_david.space.amendements) == 1
    assert user_david.space.amendements[0].num == amendements_an[0].num
    assert user_david.space.amendements[0].lecture == amendements_an[0].lecture
    assert len(user_david.space.amendements[0].events) == 1
    assert user_david.space.amendements[0].events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a mis l’amendement sur sa table"
    )


def test_spaces_release_amendement(app, amendements_an, user_david):
    from zam_repondeur.models import DBSession, Amendement, User

    with transaction.manager:
        DBSession.add(user_david)
        user_david.space.amendements.append(amendements_an[0])
        assert len(user_david.space.amendements) == 1

    email = user_david.email
    resp = app.post(
        f"/lectures/an.15.269.PO717460/spaces/{email}",
        {"num": amendements_an[0].num},
        user=email,
    )
    assert resp.status_code == 302
    assert (
        resp.location == f"https://zam.test/lectures/an.15.269.PO717460/spaces/{email}"
    )
    user_david = DBSession.query(User).filter(User.email == user_david.email).first()
    assert len(user_david.space.amendements) == 0
    amendement = (
        DBSession.query(Amendement)
        .filter(Amendement.num == amendements_an[0].num)
        .first()
    )
    assert len(amendement.events) == 1
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a remis l’amendement dans le radar"
    )


def test_spaces_transfer_amendement(app, amendements_an, user_david, user_ronan):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        DBSession.add_all([user_david, user_ronan])
        user_david.space.amendements.append(amendements_an[0])
        assert len(user_david.space.amendements) == 1
        assert len(user_ronan.space.amendements) == 0

    email = user_david.email
    resp = app.post(
        f"/lectures/an.15.269.PO717460/spaces/{email}",
        {"num": amendements_an[0].num, "target": user_ronan.email},
        user=email,
    )
    assert resp.status_code == 302
    assert (
        resp.location == f"https://zam.test/lectures/an.15.269.PO717460/spaces/{email}"
    )
    user_david = DBSession.query(User).filter(User.email == user_david.email).first()
    user_ronan = DBSession.query(User).filter(User.email == user_ronan.email).first()
    assert len(user_david.space.amendements) == 0
    assert len(user_ronan.space.amendements) == 1
    assert user_ronan.space.amendements[0].num == amendements_an[0].num
    assert user_ronan.space.amendements[0].lecture == amendements_an[0].lecture
    assert len(user_ronan.space.amendements[0].events) == 1
    assert user_ronan.space.amendements[0].events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a transféré l’amendement à « Ronan (ronan@example.com) »"
    )


def test_spaces_steal_amendement(app, amendements_an, user_david, user_ronan):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        DBSession.add_all([user_david, user_ronan])
        user_david.space.amendements.append(amendements_an[0])
        assert len(user_david.space.amendements) == 1
        assert len(user_ronan.space.amendements) == 0

    email = user_ronan.email
    resp = app.post(
        f"/lectures/an.15.269.PO717460/spaces/{email}",
        {"num": amendements_an[0].num, "target": user_ronan.email},
        user=email,
    )
    assert resp.status_code == 302
    assert (
        resp.location == f"https://zam.test/lectures/an.15.269.PO717460/spaces/{email}"
    )
    user_david = DBSession.query(User).filter(User.email == user_david.email).first()
    user_ronan = DBSession.query(User).filter(User.email == user_ronan.email).first()
    assert len(user_david.space.amendements) == 0
    assert len(user_ronan.space.amendements) == 1
    assert user_ronan.space.amendements[0].num == amendements_an[0].num
    assert user_ronan.space.amendements[0].lecture == amendements_an[0].lecture
    assert len(user_ronan.space.amendements[0].events) == 1
    assert user_ronan.space.amendements[0].events[0].render_summary() == (
        "<abbr title='ronan@example.com'>Ronan</abbr> "
        "a transféré l’amendement de « David (david@example.com) » à lui/elle-même"
    )
