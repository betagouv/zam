import transaction


def test_get_amendement_edit_form(
    app, lecture_an, amendements_an, user_david, user_david_table_an
):
    from zam_repondeur.models import DBSession

    amendement = amendements_an[1]
    with transaction.manager:
        DBSession.add(user_david_table_an)
        amendement.expose = "<p>Bla bla bla</p>"
        amendement.corps = "<p>Supprimer cet article.</p>"
        user_david_table_an.amendements.append(amendement)

    resp = app.get(
        f"/lectures/an.15.269.PO717460/amendements/{amendement.num}/amendement_edit",
        user=user_david,
    )

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    assert resp.forms["edit-amendement"].method == "POST"
    assert list(resp.forms["edit-amendement"].fields.keys()) == [
        "avis",
        "objet",
        "reponse",
        "comments",
        "save-and-transfer",
        "save",
    ]

    # Check the displayed amendement
    assert resp.parser.css_first(".title .article").text().strip() == "Article 1"

    assert resp.parser.css_first(".expose h4").text() == "Exposé"
    assert resp.parser.css_first(".expose h4 + *").text() == "Bla bla bla"

    assert resp.parser.css_first(".corps h4").text() == "Corps de l’amendement"
    assert resp.parser.css_first(".corps h4 + *").text() == "Supprimer cet article."


def test_get_amendement_edit_form_only_if_owner(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amdt = amendements_an[1]
        amdt.expose = "<p>Bla bla bla</p>"
        amdt.corps = "<p>Supprimer cet article.</p>"
        amdt.user_content.avis = "Favorable"
        DBSession.add(amdt)

    resp = app.get(
        f"/lectures/an.15.269.PO717460/amendements/{amdt.num}/amendement_edit",
        user=user_david,
    )

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check has transfer form
    assert resp.forms["transfer"].method == "POST"

    # Check the displayed reponse
    assert resp.parser.css_first(".reponse h4").text() == "Position du gouvernement"
    assert resp.parser.css_first(".reponse h4 + *").text() == "Favorable"


def test_transfer_amendement_from_edit_form(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models import DBSession, User

    # Commit our user to the database
    with transaction.manager:
        DBSession.add(user_david)

    # Our table is empty
    table = user_david.table_for(lecture_an)
    assert len(table.amendements) == 0

    amdt = amendements_an[0]

    resp = app.get(
        f"/lectures/an.15.269.PO717460/amendements/{amdt.num}/amendement_edit",
        user=user_david,
    )

    form = resp.forms["transfer"]
    resp = form.submit("submit-table")

    # We're redirected to our table
    assert resp.status_code == 302
    assert (
        resp.location
        == f"https://zam.test/lectures/an.15.269.PO717460/tables/david@example.com"
    )

    # The amendement is now on our table
    DBSession.add(amdt)
    user_david = DBSession.query(User).filter(User.email == user_david.email).first()
    table = user_david.table_for(lecture_an)
    assert len(table.amendements) == 1
    assert table.amendements[0] is amdt

    # An event was added to the amendement
    assert len(amdt.events) == 1
    assert amdt.events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> "
        "a mis l’amendement sur sa table."
    )


def test_transfer_amendement_from_edit_form_given_activity(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models import DBSession

    amdt = amendements_an[0]

    # With amendement from index.
    resp = app.get(
        f"/lectures/an.15.269.PO717460/amendements/{amdt.num}/amendement_edit",
        user=user_david,
    )

    submit_button = resp.parser.css_first('form#transfer input[type="submit"]')
    assert submit_button.attributes.get("value") == "Transférer sur ma table"
    assert submit_button.attributes.get("class") == "button primary enabled"
    link_to_transfer = resp.parser.css_first("form#transfer a")
    assert link_to_transfer.text() == "Transférer à…"
    assert link_to_transfer.attributes.get("class") == "button primary"

    # With amendement from inactive user.
    with transaction.manager:
        DBSession.add(user_ronan)
        table_ronan = user_ronan.table_for(lecture_an)
        table_ronan.amendements.append(amdt)
    resp = app.get(
        f"/lectures/an.15.269.PO717460/amendements/{amdt.num}/amendement_edit",
        user=user_david,
    )

    submit_button = resp.parser.css_first('form#transfer input[type="submit"]')
    assert submit_button.attributes.get("value") == "Transférer sur ma table"
    assert submit_button.attributes.get("class") == "button enabled warning"
    link_to_transfer = resp.parser.css_first("form#transfer a")
    assert link_to_transfer.text() == "Transférer à…"
    assert link_to_transfer.attributes.get("class") == "button warning"

    # With amendement from active user.
    user_ronan.record_activity()
    resp = app.get(
        f"/lectures/an.15.269.PO717460/amendements/{amdt.num}/amendement_edit",
        user=user_david,
    )

    submit_button = resp.parser.css_first('form#transfer input[type="submit"]')
    assert submit_button.attributes.get("value") == "Transférer sur ma table"
    assert submit_button.attributes.get("class") == "button enabled warning"
    link_to_transfer = resp.parser.css_first("form#transfer a")
    assert link_to_transfer.text() == "Transférer à…"
    assert link_to_transfer.attributes.get("class") == "button warning"

    # With amendement from amendement being edited.
    amdt.start_editing()
    resp = app.get(
        f"/lectures/an.15.269.PO717460/amendements/{amdt.num}/amendement_edit",
        user=user_david,
    )

    submit_button = resp.parser.css_first('form#transfer input[type="submit"]')
    assert submit_button.attributes.get("value") == "Forcer le transfert sur ma table"
    assert submit_button.attributes.get("class") == "button enabled danger"
    link_to_transfer = resp.parser.css_first("form#transfer a")
    assert link_to_transfer.text() == "Transférer à…"
    assert link_to_transfer.attributes.get("class") == "button danger"


def test_get_amendement_edit_form_gouvernemental(
    app, lecture_an, amendements_an, user_david, user_david_table_an
):
    from zam_repondeur.models import DBSession

    amendement = amendements_an[1]
    with transaction.manager:
        DBSession.add(user_david_table_an)
        amendement.auteur = "LE GOUVERNEMENT"
        user_david_table_an.amendements.append(amendement)

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/999/amendement_edit", user=user_david
    )

    assert resp.status_code == 200
    assert resp.content_type == "text/html"
    assert resp.forms["edit-amendement"].method == "POST"
    assert list(resp.forms["edit-amendement"].fields.keys()) == [
        "avis",
        "objet",
        "reponse",
        "comments",
        "save-and-transfer",
        "save",
    ]


def test_get_amendement_edit_form_not_found(
    app, lecture_an, amendements_an, user_david
):
    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/998/amendement_edit",
        user=user_david,
        expect_errors=True,
    )
    assert resp.status_code == 404


def test_post_amendement_edit_form(
    app, lecture_an, amendements_an, user_david, user_david_table_an
):
    from zam_repondeur.models import Amendement, DBSession

    amendement = amendements_an[1]
    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendement)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.user_content.avis is None
    assert amendement.user_content.objet is None
    assert amendement.user_content.reponse is None

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/999/amendement_edit", user=user_david
    )
    form = resp.forms["edit-amendement"]
    form["avis"] = "Favorable"
    form["objet"] = "Un objet très pertinent"
    form["reponse"] = "Une réponse <strong>très</strong> appropriée"
    form["comments"] = "Avec des <table><tr><td>commentaires</td></tr></table>"
    resp = form.submit("save")

    assert resp.status_code == 302
    assert (
        resp.location
        == "https://zam.test/lectures/an.15.269.PO717460/tables/david@example.com/#amdt-999"  # noqa
    )

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.user_content.avis == "Favorable"
    assert amendement.user_content.objet == "Un objet très pertinent"
    assert (
        amendement.user_content.reponse
        == "Une réponse <strong>très</strong> appropriée"
    )
    assert (
        amendement.user_content.comments
        == "Avec des <table><tbody><tr><td>commentaires</td></tr></tbody></table>"
    )

    # Should create events.
    assert len(amendement.events) == 4


def test_post_amendement_edit_form_reset_editing_state(
    app, lecture_an, amendements_an, user_david, user_david_table_an
):
    from zam_repondeur.models import Amendement, DBSession

    amendement = amendements_an[1]
    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendement)

    amendement.start_editing()
    assert amendement.is_being_edited

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/999/amendement_edit", user=user_david
    )
    form = resp.forms["edit-amendement"]
    form["avis"] = "Favorable"
    form["objet"] = "Un objet très pertinent"
    form["reponse"] = "Une réponse <strong>très</strong> appropriée"
    form["comments"] = "Avec des <table><tr><td>commentaires</td></tr></table>"
    resp = form.submit("save")

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert not amendement.is_being_edited


def test_post_amendement_edit_form_switch_table(
    app,
    lecture_an,
    amendements_an,
    user_david,
    user_david_table_an,
    user_ronan,
    user_ronan_table_an,
):
    from zam_repondeur.models import Amendement, DBSession

    amendement = amendements_an[1]
    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendement)

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/999/amendement_edit", user=user_david
    )
    form = resp.forms["edit-amendement"]
    form["avis"] = "Favorable"
    form["objet"] = "Un objet très pertinent"
    form["reponse"] = "Une réponse <strong>très</strong> appropriée"
    form["comments"] = "Avec des <table><tr><td>commentaires</td></tr></table>"

    # Table switch just before submitting the form.
    with transaction.manager:
        DBSession.add(user_ronan_table_an)
        user_ronan_table_an.amendements.append(amendement)

    resp = form.submit("save")

    assert resp.status_code == 302
    assert (
        resp.location
        == "https://zam.test/lectures/an.15.269.PO717460/tables/david@example.com/"
    )
    resp = resp.maybe_follow()
    assert "Les modifications n’ont PAS été enregistrées" in resp.text
    assert "Il est actuellement sur la table de Ronan" in resp.text

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.user_content.avis is None
    assert amendement.user_content.objet is None
    assert amendement.user_content.reponse is None
    assert amendement.user_content.comments is None

    # Should NOT create events.
    assert len(amendement.events) == 0


def test_post_amendement_edit_form_and_transfer(
    app, lecture_an, amendements_an, user_david, user_david_table_an
):
    from zam_repondeur.models import Amendement, DBSession

    amendement = amendements_an[1]
    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendement)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.user_content.avis is None
    assert amendement.user_content.objet is None
    assert amendement.user_content.reponse is None

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/999/amendement_edit", user=user_david
    )
    form = resp.forms["edit-amendement"]
    form["avis"] = "Favorable"
    form["objet"] = "Un objet très pertinent"
    form["reponse"] = "Une réponse <strong>très</strong> appropriée"
    form["comments"] = "Avec des <table><tr><td>commentaires</td></tr></table>"
    resp = form.submit("save-and-transfer")

    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test/lectures/an.15.269.PO717460/transfer_amendements"
        "?nums=999&from_save=1&"
        "back=https%3A%2F%2Fzam.test%2Flectures%2Fan.15.269.PO717460%2Ftables%2F"
        "david%40example.com%2F%23amdt-999"
    )

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.user_content.avis == "Favorable"
    assert amendement.user_content.objet == "Un objet très pertinent"
    assert (
        amendement.user_content.reponse
        == "Une réponse <strong>très</strong> appropriée"
    )
    assert (
        amendement.user_content.comments
        == "Avec des <table><tbody><tr><td>commentaires</td></tr></tbody></table>"
    )

    # Should create events.
    assert len(amendement.events) == 4


def test_post_amendement_edit_form_gouvernemental(
    app, lecture_an, amendements_an, user_david, user_david_table_an
):
    from zam_repondeur.models import Amendement, DBSession

    amendement = amendements_an[1]
    with transaction.manager:
        DBSession.add(user_david_table_an)
        amendement.auteur = "LE GOUVERNEMENT"
        user_david_table_an.amendements.append(amendement)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.user_content.avis is None
    assert amendement.user_content.objet is None
    assert amendement.user_content.reponse is None
    assert amendement.gouvernemental

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/999/amendement_edit", user=user_david
    )
    form = resp.forms["edit-amendement"]
    form["reponse"] = "Une réponse <strong>très</strong> appropriée"
    form["comments"] = "Avec des <table><tr><td>commentaires</td></tr></table>"
    resp = form.submit("save")

    assert resp.status_code == 302
    assert (
        resp.location
        == "https://zam.test/lectures/an.15.269.PO717460/tables/david@example.com/#amdt-999"  # noqa
    )

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.user_content.avis is None
    assert amendement.user_content.objet is None
    assert (
        amendement.user_content.reponse
        == "Une réponse <strong>très</strong> appropriée"
    )
    assert (
        amendement.user_content.comments
        == "Avec des <table><tbody><tr><td>commentaires</td></tr></tbody></table>"
    )


def test_post_amendement_edit_form_creates_event_only_if_modified(
    app, lecture_an, amendements_an, user_david, user_david_table_an
):
    from zam_repondeur.models import DBSession

    amendement = amendements_an[0]

    # Let's set a response on the amendement
    with transaction.manager:
        DBSession.add(user_david_table_an)
        amendement.user_content.avis = "Favorable"
        amendement.user_content.objet = "Un objet très pertinent"
        amendement.user_content.reponse = "Une réponse très appropriée"
        user_david_table_an.amendements.append(amendement)

    # Let's post the response edit form, but with unchanged values
    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/666/amendement_edit", user=user_david
    )
    form = resp.forms["edit-amendement"]
    form["avis"] = "Favorable"
    # Even with extra spaces.
    form["objet"] = "Un objet très pertinent  "
    form["reponse"] = "  Une réponse très appropriée"
    form.submit("save")

    # No event should be created
    DBSession.add(amendement)
    assert len(amendement.events) == 0
