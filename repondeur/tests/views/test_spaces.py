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


def test_spaces_add_amendement(app, lecture_an, amendements_an, user_david):
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
