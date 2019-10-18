import transaction


def test_amendement_start_editing(
    app, lecture_an_url, amendements_an_batch, user_david, user_david_table_an
):
    from zam_repondeur.models import DBSession, Amendement

    amendement_666 = amendements_an_batch[0]
    amendement_999 = amendements_an_batch[1]
    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendement_666)
        user_david_table_an.add_amendement(amendement_999)

    assert not amendement_666.is_being_edited
    assert not amendement_999.is_being_edited

    resp = app.post_json(
        f"{lecture_an_url}/amendements/{amendement_666.num}/start_editing",
        user=user_david,
    )

    assert resp.status_code == 200
    assert resp.content_type == "application/json"

    amendement_666 = DBSession.query(Amendement).get(amendement_666.pk)
    assert amendement_666.is_being_edited
    assert amendement_999.is_being_edited


def test_amendement_stop_editing(
    app, lecture_an_url, amendements_an_batch, user_david, user_david_table_an
):
    from zam_repondeur.models import DBSession, Amendement

    amendement_666 = amendements_an_batch[0]
    amendement_999 = amendements_an_batch[1]
    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendement_666)
        user_david_table_an.add_amendement(amendement_999)

    assert not amendement_666.is_being_edited
    assert not amendement_999.is_being_edited

    resp = app.post_json(
        f"{lecture_an_url}/amendements/{amendement_666.num}/start_editing",
        user=user_david,
    )
    resp = app.post_json(
        f"{lecture_an_url}/amendements/{amendement_666.num}/stop_editing",
        user=user_david,
    )

    assert resp.status_code == 200
    assert resp.content_type == "application/json"

    amendement_666 = DBSession.query(Amendement).get(amendement_666.pk)
    amendement_999 = DBSession.query(Amendement).get(amendement_999.pk)
    assert not amendement_666.is_being_edited
    assert not amendement_999.is_being_edited
