import transaction


def test_amendement_start_editing(
    app, lecture_an, amendements_an, user_david, user_david_table_an
):
    from zam_repondeur.models import DBSession, Amendement

    amendement = amendements_an[1]
    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendement)

    assert not amendement.is_being_edited

    resp = app.post_json(
        f"/lectures/an.15.269.PO717460/amendements/{amendement.num}/start_editing",
        user=user_david,
    )

    assert resp.status_code == 200
    assert resp.content_type == "application/json"

    amendement = DBSession.query(Amendement).get(amendement.pk)
    assert amendement.is_being_edited


def test_amendement_stop_editing(
    app, lecture_an, amendements_an, user_david, user_david_table_an
):
    from zam_repondeur.models import DBSession, Amendement

    amendement = amendements_an[1]
    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendement)

    assert not amendement.is_being_edited

    resp = app.post_json(
        f"/lectures/an.15.269.PO717460/amendements/{amendement.num}/start_editing",
        user=user_david,
    )
    resp = app.post_json(
        f"/lectures/an.15.269.PO717460/amendements/{amendement.num}/stop_editing",
        user=user_david,
    )

    assert resp.status_code == 200
    assert resp.content_type == "application/json"

    amendement = DBSession.query(Amendement).get(amendement.pk)
    assert not amendement.is_being_edited
