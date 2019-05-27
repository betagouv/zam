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
def david_has_one_amendement(
    user_david, lecture_an, user_david_table_an, amendements_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendements_an[0])

    assert len(user_david.table_for(lecture_an).amendements) == 1


@pytest.fixture
def david_has_two_amendements(
    user_david, lecture_an, user_david_table_an, amendements_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendements_an[0])
        user_david_table_an.amendements.append(amendements_an[1])

    assert len(user_david.table_for(lecture_an).amendements) == 2


def test_lecture_get_batch_amendements(
    app, amendements_an, user_david, david_has_two_amendements
):
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


def test_lecture_get_batch_amendements_not_all_on_table(
    app, amendements_an, user_david, david_has_one_amendement
):
    resp = app.get(
        "/lectures/an.15.269.PO717460/batch_amendements",
        {"nums": amendements_an},
        user=user_david,
    )

    assert resp.status_code == 302
    assert (
        resp.location
        == "https://zam.test/lectures/an.15.269.PO717460/tables/david@example.com"
    )
    resp = resp.follow()
    assert (
        "Tous les amendements doivent être sur votre table pour pouvoir les associer."
        in resp.text
    )


def test_lecture_post_batch_set_amendements(
    app, lecture_an, amendements_an, user_david, david_has_two_amendements
):
    from zam_repondeur.models import Amendement, DBSession

    DBSession.add_all(amendements_an)
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


def test_lecture_post_batch_set_amendements_not_all_on_table(
    app, lecture_an, amendements_an, user_david, david_has_two_amendements
):
    from zam_repondeur.models import Amendement, DBSession

    DBSession.add_all(amendements_an)
    assert not amendements_an[0].batch
    assert not amendements_an[1].batch

    resp = app.get(
        "/lectures/an.15.269.PO717460/batch_amendements",
        {"nums": amendements_an},
        user=user_david,
    )
    form = resp.form

    # Let's remove an amendement from the table before submission.
    with transaction.manager:
        amendements_an[0].user_table = None
        DBSession.add(amendements_an[0])

    resp = form.submit("submit-to")

    # We are redirected to our table.
    assert resp.status_code == 302
    assert (
        resp.location
        == f"https://zam.test/lectures/an.15.269.PO717460/tables/{user_david.email}"
    )
    resp = resp.follow()
    assert (
        "Tous les amendements doivent être sur votre table pour pouvoir les associer."
        in resp.text
    )

    # Reload amendements as they were updated in another transaction.
    amendement_666 = Amendement.get(lecture_an, amendements_an[0].num)
    amendement_999 = Amendement.get(lecture_an, amendements_an[1].num)

    # No amendement has any batch set.
    assert not amendement_666.batch
    assert not amendement_999.batch


def test_lecture_post_batch_unset_amendement(
    app, lecture_an, amendements_an, user_david, david_has_two_amendements
):
    from zam_repondeur.models import Amendement, DBSession

    DBSession.add_all(amendements_an)
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


def test_lecture_post_batch_reset_amendement(
    app,
    lecture_an,
    article1_an,
    amendements_an,
    user_david,
    user_david_table_an,
    david_has_two_amendements,
):
    from zam_repondeur.models import Amendement, DBSession

    DBSession.add_all(amendements_an)
    assert not amendements_an[0].batch
    assert not amendements_an[1].batch

    with transaction.manager:
        amendement_777 = Amendement.create(
            lecture=lecture_an, article=article1_an, num=777
        )
        user_david_table_an.amendements.append(amendement_777)
        assert not amendement_777.batch

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

    # Then we re-associate two others (containing the first one)
    resp = app.get(
        "/lectures/an.15.269.PO717460/batch_amendements",
        {"nums": [amendement_666, amendement_777]},
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

    # Reload amendement as it was updated in another transaction.
    amendement_666 = Amendement.get(lecture_an, amendements_an[0].num)
    amendement_999 = Amendement.get(lecture_an, amendements_an[1].num)
    amendement_777 = Amendement.get(lecture_an, amendement_777.num)

    # A new batch is created and 999 has no batch anymore.
    assert amendement_666.batch.pk == 2
    assert not amendement_999.batch
    assert amendement_777.batch.pk == 2
    assert amendement_666.batch.amendements == [amendement_666, amendement_777]

    # We should have events for all actions.
    assert len(amendement_666.events) == 3
    assert amendement_666.events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a placé l’amendement dans un lot avec les amendements numéro 777."
    )
    assert amendement_666.events[1].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a sorti l’amendement du lot dans lequel il était."
    )
    assert amendement_666.events[2].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a placé l’amendement dans un lot avec les amendements numéro 999."
    )
    assert len(amendement_999.events) == 2
    assert amendement_999.events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a sorti l’amendement du lot dans lequel il était."
    )
    assert amendement_999.events[1].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a placé l’amendement dans un lot avec les amendements numéro 666."
    )
    assert len(amendement_777.events) == 1
    assert amendement_777.events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a placé l’amendement dans un lot avec les amendements numéro 666."
    )
