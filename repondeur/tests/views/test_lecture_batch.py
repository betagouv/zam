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
        user_david_table_an.add_amendement(amendements_an[0])

    assert len(user_david.table_for(lecture_an).amendements) == 1


@pytest.fixture
def david_has_two_amendements(
    user_david, lecture_an, user_david_table_an, amendements_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendements_an[0])
        user_david_table_an.add_amendement(amendements_an[1])

    assert len(user_david.table_for(lecture_an).amendements) == 2


def test_lecture_get_batch_amendements(
    app, amendements_an, user_david, david_has_two_amendements
):
    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": amendements_an},
        user=user_david,
    )

    assert resp.status_code == 200
    assert "Nº\xa0666" in resp.parser.css_first(".amendements li").text()
    assert "checked" in resp.parser.css_first(".amendements li input").attributes

    form = resp.forms["batch-amendements"]
    assert form.method == "POST"
    assert list(form.fields.keys()) == ["n", "submit-to"]
    assert form.fields["n"][0].value == "666"
    assert form.fields["n"][1].value == "999"


def test_lecture_get_batch_amendements_not_all_on_table(
    app, amendements_an, user_david, david_has_one_amendement
):
    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": amendements_an},
        user=user_david,
    )

    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test"
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/tables/david@exemple.gouv.fr/"
    )
    resp = resp.follow()
    assert (
        "Tous les amendements doivent être sur votre table pour pouvoir les associer."
        in resp.text
    )


def test_lecture_get_batch_amendements_only_one_reponse(
    app, amendements_an, user_david, david_has_two_amendements
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendements_an[0].user_content.avis = "Favorable"
        DBSession.add_all(amendements_an)

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": amendements_an},
        user=user_david,
    )

    assert resp.status_code == 200


def test_lecture_get_batch_amendements_same_reponses(
    app, amendements_an, user_david, david_has_two_amendements
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendements_an[0].user_content.avis = "Favorable"
        amendements_an[1].user_content.avis = "Favorable"
        DBSession.add_all(amendements_an)

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": amendements_an},
        user=user_david,
    )

    assert resp.status_code == 200


def test_lecture_get_batch_amendements_different_reponses(
    app, lecture_an, amendements_an, user_david, david_has_two_amendements
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendements_an[0].user_content.avis = "Favorable"
        amendements_an[1].user_content.avis = "Défavorable"
        DBSession.add_all(amendements_an)

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": amendements_an},
        user=user_david,
    )

    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test"
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/tables/david@exemple.gouv.fr/"
    )
    resp = resp.follow()
    assert (
        "Tous les amendements doivent avoir les mêmes réponses et commentaires avant "
        "de pouvoir être associés."
    ) in resp.text


def test_lecture_get_batch_amendements_same_reponses_different_comments(
    app, lecture_an, amendements_an, user_david, david_has_two_amendements
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendements_an[0].user_content.avis = "Favorable"
        amendements_an[1].user_content.avis = "Favorable"
        amendements_an[1].user_content.comments = "Commentaire"
        DBSession.add_all(amendements_an)

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": amendements_an},
        user=user_david,
    )

    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test"
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/tables/david@exemple.gouv.fr/"
    )
    resp = resp.follow()
    assert (
        "Tous les amendements doivent avoir les mêmes réponses et commentaires avant "
        "de pouvoir être associés."
    ) in resp.text


def test_lecture_get_batch_amendements_different_articles(
    app,
    lecture_an,
    article7bis_an,
    amendements_an,
    user_david,
    david_has_two_amendements,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendements_an[0].article = article7bis_an
        DBSession.add_all(amendements_an)

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": amendements_an},
        user=user_david,
    )

    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test"
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/tables/david@exemple.gouv.fr/"
    )
    resp = resp.follow()
    assert (
        "Tous les amendements doivent être relatifs au même article "
        "pour pouvoir être associés."
    ) in resp.text


def test_lecture_get_batch_amendements_same_mission(
    app,
    lecture_an,
    article7bis_an,
    amendements_an,
    user_david,
    david_has_two_amendements,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendements_an[0].mission_titre = "test"
        amendements_an[1].mission_titre = "test"
        DBSession.add_all(amendements_an)

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": amendements_an},
        user=user_david,
    )

    assert resp.status_code == 200


def test_lecture_get_batch_amendements_different_mission(
    app,
    lecture_an,
    article7bis_an,
    amendements_an,
    user_david,
    david_has_two_amendements,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendements_an[0].mission_titre = "test"
        DBSession.add_all(amendements_an)

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": amendements_an},
        user=user_david,
    )

    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test"
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/tables/david@exemple.gouv.fr/"
    )
    resp = resp.follow()
    assert (
        "Tous les amendements doivent être relatifs à la même mission "
        "pour pouvoir être associés."
    ) in resp.text


def test_lecture_post_batch_set_amendements(
    app, lecture_an, amendements_an, user_david, david_has_two_amendements
):
    from zam_repondeur.models import Amendement, DBSession

    DBSession.add_all(amendements_an)
    assert not amendements_an[0].location.batch
    assert not amendements_an[1].location.batch

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": amendements_an},
        user=user_david,
    )
    resp = resp.forms["batch-amendements"].submit("submit-to")

    # We're redirected to our table
    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test/"
        "dossiers/plfss-2018/"
        "lectures/an.15.269.PO717460/"
        "tables/david@exemple.gouv.fr/"
    )

    # Reload amendements as they were updated in another transaction
    amendement_666 = Amendement.get(lecture_an, amendements_an[0].num)
    amendement_999 = Amendement.get(lecture_an, amendements_an[1].num)

    # Both amendements are in the same batch
    assert amendement_666.location.batch.pk == 1
    assert amendement_999.location.batch.pk == 1
    assert amendement_666.location.batch.amendements == [amendement_666, amendement_999]

    # An event was added to both amendements
    assert len(amendement_666.events) == 1
    assert amendement_666.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a placé cet amendement dans un lot avec l’amendement 999."
    )
    assert len(amendement_999.events) == 1
    assert amendement_999.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a placé cet amendement dans un lot avec l’amendement 666."
    )


def test_lecture_post_batch_set_amendements_not_all_on_table(
    app, lecture_an, amendements_an, user_david, david_has_two_amendements
):
    from zam_repondeur.models import Amendement, DBSession

    DBSession.add_all(amendements_an)
    assert not amendements_an[0].location.batch
    assert not amendements_an[1].location.batch

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": amendements_an},
        user=user_david,
    )
    form = resp.forms["batch-amendements"]

    # Let's remove an amendement from the table before submission.
    with transaction.manager:
        amendements_an[0].location.user_table = None
        DBSession.add(amendements_an[0])

    resp = form.submit("submit-to")

    # We are redirected to our table.
    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test/"
        "dossiers/plfss-2018/"
        "lectures/an.15.269.PO717460/"
        "tables/david@exemple.gouv.fr/"
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
    assert not amendement_666.location.batch
    assert not amendement_999.location.batch


def test_lecture_post_batch_set_amendements_only_one_reponse(
    app, lecture_an, amendements_an, user_david, david_has_two_amendements
):
    from zam_repondeur.models import Amendement, DBSession

    DBSession.add_all(amendements_an)
    assert not amendements_an[0].location.batch
    assert not amendements_an[1].location.batch

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": amendements_an},
        user=user_david,
    )
    form = resp.forms["batch-amendements"]

    # Let's change reponses of the first amendement before submission.
    with transaction.manager:
        amendements_an[0].user_content.avis = "Favorable"
        amendements_an[0].user_content.objet = "Quelque chose"
        amendements_an[0].user_content.reponse = "<p>Bla bla bla</p>"
        amendements_an[0].user_content.comments = "Lorem ipsum"
        DBSession.add_all(amendements_an)

    resp = form.submit("submit-to")

    # We're redirected to our table
    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test/"
        "dossiers/plfss-2018/"
        "lectures/an.15.269.PO717460/"
        "tables/david@exemple.gouv.fr/"
    )

    # Reload amendements as they were updated in another transaction
    amendement_666 = Amendement.get(lecture_an, amendements_an[0].num)
    amendement_999 = Amendement.get(lecture_an, amendements_an[1].num)

    # Both amendements are in the same batch
    assert amendement_666.location.batch.pk == 1
    assert amendement_999.location.batch.pk == 1

    # Both amendements should have the same avis
    assert amendement_666.user_content.avis == "Favorable"
    assert amendement_999.user_content.avis == "Favorable"

    # Both amendements should keep their html content
    assert amendement_666.user_content.reponse == "<p>Bla bla bla</p>"
    assert amendement_999.user_content.reponse == "<p>Bla bla bla</p>"

    # An event was added to the second one
    assert len(amendement_999.events) == 5
    assert [
        str(event.render_summary()) for event in reversed(amendement_999.events)
    ] == [
        (
            "<abbr title='david@exemple.gouv.fr'>David</abbr> a placé cet amendement"
            " dans un lot avec l’amendement 666."
        ),
        (
            "<abbr title='david@exemple.gouv.fr'>David</abbr> a mis l’avis "
            "à « Favorable »."
        ),
        "<abbr title='david@exemple.gouv.fr'>David</abbr> a ajouté l’objet.",
        "<abbr title='david@exemple.gouv.fr'>David</abbr> a ajouté la réponse.",
        "<abbr title='david@exemple.gouv.fr'>David</abbr> a ajouté des commentaires.",
    ]


def test_lecture_post_batch_set_amendements_update_all_user_content(
    app, lecture_an, amendements_an, user_david, david_has_two_amendements
):
    from zam_repondeur.models import Amendement, DBSession

    DBSession.add_all(amendements_an)
    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": amendements_an},
        user=user_david,
    )
    form = resp.forms["batch-amendements"]

    # Let's change user content of the first amendement before submission.
    with transaction.manager:
        amendements_an[0].user_content.avis = "Favorable"
        amendements_an[0].user_content.objet = "Objet"
        amendements_an[0].user_content.reponse = "Contenu"
        amendements_an[0].user_content.comments = "Commentaire"
        DBSession.add_all(amendements_an)

    resp = form.submit("submit-to")

    # Reload amendements as they were updated in another transaction
    amendement_666 = Amendement.get(lecture_an, amendements_an[0].num)
    amendement_999 = Amendement.get(lecture_an, amendements_an[1].num)

    # Both amendements should have the same user content
    assert amendement_666.user_content.avis == "Favorable"
    assert amendement_666.user_content.objet == "Objet"
    assert amendement_666.user_content.reponse == "Contenu"
    assert amendement_666.user_content.comments == "Commentaire"
    assert amendement_999.user_content.avis == "Favorable"
    assert amendement_999.user_content.objet == "Objet"
    assert amendement_999.user_content.reponse == "Contenu"
    assert amendement_999.user_content.comments == "Commentaire"


def test_lecture_post_batch_set_amendements_same_reponses(
    app, lecture_an, amendements_an, user_david, david_has_two_amendements
):
    from zam_repondeur.models import Amendement, DBSession

    DBSession.add_all(amendements_an)
    assert not amendements_an[0].location.batch
    assert not amendements_an[1].location.batch

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": amendements_an},
        user=user_david,
    )
    form = resp.forms["batch-amendements"]

    # Let's change reponses of the amendements before submission.
    with transaction.manager:
        amendements_an[0].user_content.avis = "Favorable"
        amendements_an[1].user_content.avis = "Favorable"
        DBSession.add_all(amendements_an)

    resp = form.submit("submit-to")

    # We're redirected to our table
    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test/"
        "dossiers/plfss-2018/"
        "lectures/an.15.269.PO717460/"
        "tables/david@exemple.gouv.fr/"
    )

    # Reload amendements as they were updated in another transaction
    amendement_666 = Amendement.get(lecture_an, amendements_an[0].num)
    amendement_999 = Amendement.get(lecture_an, amendements_an[1].num)

    # Both amendements are in the same batch
    assert amendement_666.location.batch.pk == 1
    assert amendement_999.location.batch.pk == 1


def test_lecture_post_batch_set_amendements_different_reponses(
    app, lecture_an, amendements_an, user_david, david_has_two_amendements
):
    from zam_repondeur.models import Amendement, DBSession

    DBSession.add_all(amendements_an)
    assert not amendements_an[0].location.batch
    assert not amendements_an[1].location.batch

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": amendements_an},
        user=user_david,
    )
    form = resp.forms["batch-amendements"]

    # Let's change reponses of the amendements before submission.
    with transaction.manager:
        amendements_an[0].user_content.avis = "Favorable"
        amendements_an[1].user_content.avis = "Défavorable"
        DBSession.add_all(amendements_an)

    resp = form.submit("submit-to")

    # We are redirected to our table.
    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test/"
        "dossiers/plfss-2018/"
        "lectures/an.15.269.PO717460/"
        "tables/david@exemple.gouv.fr/"
    )
    resp = resp.follow()
    assert (
        "Tous les amendements doivent avoir les mêmes réponses et commentaires avant "
        "de pouvoir être associés." in resp.text
    )

    # Reload amendements as they were updated in another transaction.
    amendement_666 = Amendement.get(lecture_an, amendements_an[0].num)
    amendement_999 = Amendement.get(lecture_an, amendements_an[1].num)

    # No amendement has any batch set.
    assert not amendement_666.location.batch
    assert not amendement_999.location.batch


def test_lecture_post_batch_set_amendements_same_reponses_different_comments(
    app, lecture_an, amendements_an, user_david, david_has_two_amendements
):
    from zam_repondeur.models import Amendement, DBSession

    DBSession.add_all(amendements_an)
    assert not amendements_an[0].location.batch
    assert not amendements_an[1].location.batch

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": amendements_an},
        user=user_david,
    )
    form = resp.forms["batch-amendements"]

    # Let's change reponses of the amendements before submission.
    with transaction.manager:
        amendements_an[0].user_content.avis = "Favorable"
        amendements_an[1].user_content.avis = "Favorable"
        amendements_an[1].user_content.avis = "Commentaire"
        DBSession.add_all(amendements_an)

    resp = form.submit("submit-to")

    # We are redirected to our table.
    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test/"
        "dossiers/plfss-2018/"
        "lectures/an.15.269.PO717460/"
        "tables/david@exemple.gouv.fr/"
    )
    resp = resp.follow()
    assert (
        "Tous les amendements doivent avoir les mêmes réponses et commentaires avant "
        "de pouvoir être associés." in resp.text
    )

    # Reload amendements as they were updated in another transaction.
    amendement_666 = Amendement.get(lecture_an, amendements_an[0].num)
    amendement_999 = Amendement.get(lecture_an, amendements_an[1].num)

    # No amendement has any batch set.
    assert not amendement_666.location.batch
    assert not amendement_999.location.batch


def test_lecture_post_batch_set_amendements_different_articles(
    app,
    lecture_an,
    article7bis_an,
    amendements_an,
    user_david,
    david_has_two_amendements,
):
    from zam_repondeur.models import Amendement, DBSession

    DBSession.add_all(amendements_an)
    assert not amendements_an[0].location.batch
    assert not amendements_an[1].location.batch

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": amendements_an},
        user=user_david,
    )
    form = resp.forms["batch-amendements"]

    # Let's change article of the first amendement before submission.
    with transaction.manager:
        amendements_an[0].article = article7bis_an
        DBSession.add_all(amendements_an)

    resp = form.submit("submit-to")

    # We are redirected to our table.
    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test/"
        "dossiers/plfss-2018/"
        "lectures/an.15.269.PO717460/"
        "tables/david@exemple.gouv.fr/"
    )
    resp = resp.follow()
    assert (
        "Tous les amendements doivent être relatifs au même article "
        "pour pouvoir être associés." in resp.text
    )

    # Reload amendements as they were updated in another transaction.
    amendement_666 = Amendement.get(lecture_an, amendements_an[0].num)
    amendement_999 = Amendement.get(lecture_an, amendements_an[1].num)

    # No amendement has any batch set.
    assert not amendement_666.location.batch
    assert not amendement_999.location.batch


def test_lecture_post_batch_unset_amendement(
    app, lecture_an, amendements_an, user_david, david_has_two_amendements
):
    from zam_repondeur.models import Amendement, DBSession
    from zam_repondeur.models.events.amendement import BatchUnset

    DBSession.add_all(amendements_an)
    assert not amendements_an[0].location.batch
    assert not amendements_an[1].location.batch

    # First we associate two amendements
    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": amendements_an},
        user=user_david,
    )
    form = resp.forms["batch-amendements"]
    resp = form.submit("submit-to")

    # Reload amendement as it was updated in another transaction
    amendement_666 = Amendement.get(lecture_an, amendements_an[0].num)
    amendement_999 = Amendement.get(lecture_an, amendements_an[1].num)

    # Both amendements are in the same batch
    assert amendement_666.location.batch.pk == 1
    assert amendement_999.location.batch.pk == 1
    assert amendement_666.location.batch.amendements == [amendement_666, amendement_999]

    # Then we deassociate just one
    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": amendement_666},
        user=user_david,
    )
    form = resp.forms["batch-amendements"]
    resp = form.submit("submit-to")

    # We're redirected to our table
    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test/"
        "dossiers/plfss-2018/"
        "lectures/an.15.269.PO717460/"
        "tables/david@exemple.gouv.fr/"
    )

    # Reload amendement as it was updated in another transaction
    amendement_666 = Amendement.get(lecture_an, amendements_an[0].num)
    amendement_999 = Amendement.get(lecture_an, amendements_an[1].num)

    # Both amendements are now without any batch
    assert not amendement_666.location.batch
    assert not amendement_999.location.batch

    # An event was added to both amendements
    assert len(amendement_666.events) == 2
    assert isinstance(amendement_666.events[0], BatchUnset)
    assert amendement_666.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a sorti cet amendement du lot dans lequel il était."
    )
    assert len(amendement_999.events) == 2
    assert isinstance(amendement_999.events[0], BatchUnset)
    assert amendement_999.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a sorti cet amendement du lot dans lequel il était."
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
    assert not amendements_an[0].location.batch
    assert not amendements_an[1].location.batch

    with transaction.manager:
        amendement_777 = Amendement.create(
            lecture=lecture_an, article=article1_an, num="777"
        )
        user_david_table_an.add_amendement(amendement_777)
        assert not amendement_777.location.batch

    # First we associate two amendements
    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": amendements_an},
        user=user_david,
    )
    form = resp.forms["batch-amendements"]
    resp = form.submit("submit-to")

    # Reload amendement as it was updated in another transaction
    amendement_666 = Amendement.get(lecture_an, amendements_an[0].num)
    amendement_999 = Amendement.get(lecture_an, amendements_an[1].num)

    # Both amendements are in the same batch
    assert amendement_666.location.batch.pk == 1
    assert amendement_999.location.batch.pk == 1
    assert amendement_666.location.batch.amendements == [amendement_666, amendement_999]

    # Then we re-associate two others (containing the first one)
    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/batch_amendements",
        {"n": [amendement_666, amendement_777]},
        user=user_david,
    )
    form = resp.forms["batch-amendements"]
    resp = form.submit("submit-to")

    # We're redirected to our table
    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test/"
        "dossiers/plfss-2018/"
        "lectures/an.15.269.PO717460/"
        "tables/david@exemple.gouv.fr/"
    )

    # Reload amendements as they were updated in another transaction.
    amendement_666 = Amendement.get(lecture_an, "666")
    amendement_999 = Amendement.get(lecture_an, "999")
    amendement_777 = Amendement.get(lecture_an, "777")

    # A new batch is created and 999 is also included.
    assert amendement_666.location.batch.pk == 2
    assert amendement_999.location.batch.pk == 2
    assert amendement_777.location.batch.pk == 2
    assert amendement_666.location.batch.amendements == [
        amendement_666,
        amendement_999,
        amendement_777,
    ]

    # We should have events for all actions.
    assert len(amendement_666.events) == 3
    assert amendement_666.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a placé cet amendement dans un lot avec les amendements 999 et 777."
    )
    assert amendement_666.events[1].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a sorti cet amendement du lot dans lequel il était."
    )
    assert amendement_666.events[2].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a placé cet amendement dans un lot avec l’amendement 999."
    )

    assert len(amendement_999.events) == 3
    assert amendement_999.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a placé cet amendement dans un lot avec les amendements 666 et 777."
    )
    assert amendement_999.events[1].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a sorti cet amendement du lot dans lequel il était."
    )
    assert amendement_999.events[2].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a placé cet amendement dans un lot avec l’amendement 666."
    )

    assert len(amendement_777.events) == 1
    assert amendement_777.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a placé cet amendement dans un lot avec les amendements 666 et 999."
    )
