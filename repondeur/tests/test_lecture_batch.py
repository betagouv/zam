import transaction


def test_lecture_get_batch_amendements(app, amendements_an, user_david):
    resp = app.get(
        "/lectures/an.15.269.PO717460/batch_amendements",
        {"nums": amendements_an},
        user=user_david,
    )

    assert resp.status_code == 200
    assert "Nº 666" in resp.parser.css_first(".amendements li").text()
    assert "checked" in resp.parser.css_first(".amendements li input").attributes

    assert resp.form.method == "POST"
    assert list(resp.form.fields.keys()) == ["nums", "submit-to"]
    assert resp.form.fields["nums"][0].value == "666"
    assert resp.form.fields["nums"][1].value == "999"


def test_lecture_post_batch_set_amendements(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        DBSession.add_all(amendements_an)
        DBSession.add(user_david)
        assert not amendements_an[0].batch
        assert not amendements_an[1].batch

    resp = app.get(
        "/lectures/an.15.269.PO717460/batch_amendements",
        {"nums": amendements_an},
        user=user_david,
    )
    form = resp.form
    resp = form.submit("submit-to")

    # We're redirected to our table
    assert resp.status_code == 302
    assert (
        resp.location
        == f"https://zam.test/lectures/an.15.269.PO717460/tables/{user_david.email}"
    )

    # Reload amendements as they were updated in another transaction
    amendement_666 = Amendement.get(lecture_an, amendements_an[0].num)
    amendement_999 = Amendement.get(lecture_an, amendements_an[1].num)

    # Both amendements are in the same batch
    assert amendement_666.batch.pk == 1
    assert amendement_999.batch.pk == 1
    assert amendement_666.batch.amendements == [amendement_666, amendement_999]

    # An event was added to both amendements
    assert len(amendement_666.events) == 1
    assert amendement_666.events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a placé l’amendement dans un lot avec les amendements numéro 999."
    )
    assert len(amendement_999.events) == 1
    assert amendement_999.events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a placé l’amendement dans un lot avec les amendements numéro 666."
    )


def test_lecture_post_batch_unset_amendement(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models import Amendement, DBSession

    DBSession.add_all(amendements_an)
    DBSession.add(user_david)
    assert not amendements_an[0].batch
    assert not amendements_an[1].batch

    # First we associate two amendements
    resp = app.get(
        "/lectures/an.15.269.PO717460/batch_amendements",
        {"nums": amendements_an},
        user=user_david,
    )
    form = resp.form
    resp = form.submit("submit-to")

    # Reload amendement as it was updated in another transaction
    amendement_666 = Amendement.get(lecture_an, amendements_an[0].num)
    amendement_999 = Amendement.get(lecture_an, amendements_an[1].num)

    # Both amendements are in the same batch
    assert amendement_666.batch.pk == 1
    assert amendement_999.batch.pk == 1
    assert amendement_666.batch.amendements == [amendement_666, amendement_999]

    # Then we deassociate just one
    resp = app.get(
        "/lectures/an.15.269.PO717460/batch_amendements",
        {"nums": amendement_666},
        user=user_david,
    )
    form = resp.form
    resp = form.submit("submit-to")

    # We're redirected to our table
    assert resp.status_code == 302
    assert (
        resp.location
        == f"https://zam.test/lectures/an.15.269.PO717460/tables/{user_david.email}"
    )

    # Reload amendement as it was updated in another transaction
    amendement_666 = Amendement.get(lecture_an, amendements_an[0].num)
    amendement_999 = Amendement.get(lecture_an, amendements_an[1].num)

    # Both amendements are now without any batch
    assert not amendement_666.batch
    assert not amendement_999.batch

    # An event was added to both amendements
    assert len(amendement_666.events) == 2
    assert amendement_666.events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a sorti l’amendement du lot dans lequel il était."
    )
    assert len(amendement_999.events) == 2
    assert amendement_999.events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a sorti l’amendement du lot dans lequel il était."
    )
