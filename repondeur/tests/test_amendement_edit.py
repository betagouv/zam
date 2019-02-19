import transaction


def test_get_amendement_edit_form(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession

    amendement = amendements_an[1]
    with transaction.manager:
        amendement.expose = "<p>Bla bla bla</p>"
        amendement.corps = "<p>Supprimer cet article.</p>"
        DBSession.add(amendement)
        table = user_david.table_for(lecture_an)
        table.amendements.append(amendement)

    resp = app.get(
        f"/lectures/an.15.269.PO717460/amendements/{amendement.num}/amendement_edit",
        user=user_david.email,
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
    assert resp.forms["prefill-reponse"].method == "POST"

    # Check the displayed amendement
    assert resp.parser.css_first(".expose h4").text() == "Exposé"
    assert resp.parser.css_first(".expose h4 + *").text() == "Bla bla bla"

    assert resp.parser.css_first(".corps h4").text() == "Corps de l’amendement"
    assert resp.parser.css_first(".corps h5").text() == "Article 1"
    assert resp.parser.css_first(".corps h5 + *").text() == "Supprimer cet article."


def test_get_amendement_edit_form_only_if_owner(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amdt = amendements_an[1]
        amdt.expose = "<p>Bla bla bla</p>"
        amdt.corps = "<p>Supprimer cet article.</p>"
        amdt.user_content.avis = "Favorable"
        DBSession.add(amdt)

    resp = app.get(
        f"/lectures/an.15.269.PO717460/amendements/{amdt.num}/amendement_edit",
        user="user@example.com",
    )

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check no prefill form
    assert "prefill-reponse" not in resp.forms

    # Check has transfer form
    assert resp.forms["transfer"].method == "POST"

    # Check the displayed reponse
    assert resp.parser.css_first(".reponse h4").text() == "Position du gouvernement"
    assert resp.parser.css_first(".reponse h4 + *").text() == "Favorable"


def test_transfer_amendement_from_edit_form(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        DBSession.add(user_david)
        table = user_david.table_for(lecture_an)
        assert len(table.amendements) == 0

    amdt = amendements_an[0]
    resp = app.get(
        f"/lectures/an.15.269.PO717460/amendements/{amdt.num}/amendement_edit",
        user=user_david.email,
    )

    form = resp.forms["transfer"]
    resp = form.submit("submit-table")

    assert resp.status_code == 302
    assert (
        resp.location
        == f"https://zam.test/lectures/an.15.269.PO717460/tables/david@example.com"
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


def test_get_amendement_edit_form_gouvernemental(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models import DBSession

    amendement = amendements_an[1]
    with transaction.manager:
        amendement.auteur = "LE GOUVERNEMENT"
        DBSession.add(amendement)
        table = user_david.table_for(lecture_an)
        table.amendements.append(amendement)

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/999/amendement_edit",
        user=user_david.email,
    )

    assert resp.status_code == 200
    assert resp.content_type == "text/html"
    assert resp.forms["edit-amendement"].method == "POST"
    assert list(resp.forms["edit-amendement"].fields.keys()) == [
        "objet",
        "reponse",
        "comments",
        "save-and-transfer",
        "save",
    ]
    assert resp.forms.get("prefill-reponse") is None


def test_get_amendement_edit_form_not_found(app, lecture_an, amendements_an):
    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/998/amendement_edit",
        user="user@example.com",
        expect_errors=True,
    )
    assert resp.status_code == 404


def test_post_amendement_edit_form(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import Amendement, DBSession

    amendement = amendements_an[1]
    with transaction.manager:
        DBSession.add(amendement)
        table = user_david.table_for(lecture_an)
        table.amendements.append(amendement)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.user_content.avis is None
    assert amendement.user_content.objet is None
    assert amendement.user_content.reponse is None
    initial_amendement_modified_at = amendement.modified_at

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/999/amendement_edit",
        user=user_david.email,
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
    assert initial_amendement_modified_at < amendement.modified_at

    # Should create events.
    assert len(amendement.events) == 3


def test_post_amendement_edit_form_and_transfer(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models import Amendement, DBSession

    amendement = amendements_an[1]
    with transaction.manager:
        DBSession.add(amendement)
        table = user_david.table_for(lecture_an)
        table.amendements.append(amendement)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.user_content.avis is None
    assert amendement.user_content.objet is None
    assert amendement.user_content.reponse is None
    initial_amendement_modified_at = amendement.modified_at

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/999/amendement_edit",
        user=user_david.email,
    )
    form = resp.forms["edit-amendement"]
    form["avis"] = "Favorable"
    form["objet"] = "Un objet très pertinent"
    form["reponse"] = "Une réponse <strong>très</strong> appropriée"
    form["comments"] = "Avec des <table><tr><td>commentaires</td></tr></table>"
    resp = form.submit("save-and-transfer")

    assert resp.status_code == 302
    assert (
        resp.location
        == "https://zam.test/lectures/an.15.269.PO717460/transfer_amendements?nums=999"
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
    assert initial_amendement_modified_at < amendement.modified_at

    # Should create events.
    assert len(amendement.events) == 3


def test_post_amendement_edit_form_gouvernemental(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models import Amendement, DBSession

    amendement = amendements_an[1]
    with transaction.manager:
        amendement.auteur = "LE GOUVERNEMENT"
        DBSession.add(amendement)
        table = user_david.table_for(lecture_an)
        table.amendements.append(amendement)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.user_content.avis is None
    assert amendement.user_content.objet is None
    assert amendement.user_content.reponse is None
    assert amendement.gouvernemental
    initial_amendement_modified_at = amendement.modified_at

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/999/amendement_edit",
        user=user_david.email,
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
    assert amendement.user_content.avis == ""
    assert amendement.user_content.objet is None
    assert (
        amendement.user_content.reponse
        == "Une réponse <strong>très</strong> appropriée"
    )
    assert (
        amendement.user_content.comments
        == "Avec des <table><tbody><tr><td>commentaires</td></tr></tbody></table>"
    )
    assert initial_amendement_modified_at < amendement.modified_at


def test_post_amendement_edit_form_updates_modification_dates_only_if_modified(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models import Amendement, DBSession, Lecture

    amendement = amendements_an[0]

    # Let's remember the initial modification dates
    initial_lecture_modified_at = lecture_an.modified_at
    initial_amendement_modified_at = amendement.modified_at

    # Let's set a response on the amendement
    with transaction.manager:
        amendement.user_content.avis = "Favorable"
        amendement.user_content.objet = "Un objet très pertinent"
        amendement.user_content.reponse = "Une réponse très appropriée"
        DBSession.add(amendement)
        table = user_david.table_for(lecture_an)
        table.amendements.append(amendement)

    # Let's post the response edit form, but with unchanged values
    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/666/amendement_edit",
        user=user_david.email,
    )
    form = resp.forms["edit-amendement"]
    form["avis"] = "Favorable"
    # Even with extra spaces.
    form["objet"] = "Un objet très pertinent  "
    form["reponse"] = "  Une réponse très appropriée"
    form.submit("save")

    # The lecture modification date should not be updated
    lecture = Lecture.get(
        chambre=lecture_an.chambre,
        session=lecture_an.session,
        num_texte=lecture_an.num_texte,
        partie=None,
        organe=lecture_an.organe,
    )
    assert initial_lecture_modified_at == lecture.modified_at

    # The amendement modification date should not be updated
    amendement = (
        DBSession.query(Amendement)
        .filter(Amendement.num == amendements_an[0].num)
        .first()
    )
    assert initial_amendement_modified_at == amendement.modified_at

    # And no event should be created.
    assert len(amendement.events) == 0
