import transaction


def test_get_reponse_edit_form(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amdt = amendements_an[1]
        amdt.expose = "<p>Bla bla bla</p>"
        amdt.corps = "<p>Supprimer cet article.</p>"
        DBSession.add(amdt)

    resp = app.get(
        f"http://localhost/lectures/an.15.269.PO717460/amendements/{amdt.num}/reponse"
    )

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    assert resp.forms["edit-reponse"].method == "POST"
    assert list(resp.forms["edit-reponse"].fields.keys()) == [
        "avis",
        "objet",
        "reponse",
        "affectation",
        "comments",
        "submit",
    ]
    assert resp.forms["prefill-reponse"].method == "POST"

    # Check the displayed amendement
    assert resp.parser.css_first(".expose h4").text() == "Exposé"
    assert resp.parser.css_first(".expose h4 + *").text() == "Bla bla bla"

    assert resp.parser.css_first(".corps h4").text() == "Corps de l’amendement"
    assert resp.parser.css_first(".corps h5").text() == "Article 1"
    assert resp.parser.css_first(".corps h5 + *").text() == "Supprimer cet article."


def test_get_reponse_edit_form_gouvernemental(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    amendement = amendements_an[1]
    with transaction.manager:
        amendement.auteur = "LE GOUVERNEMENT"
        DBSession.add(amendement)

    resp = app.get(
        "http://localhost/lectures/an.15.269.PO717460/amendements/999/reponse"
    )

    assert resp.status_code == 200
    assert resp.content_type == "text/html"
    assert resp.forms["edit-reponse"].method == "POST"
    assert list(resp.forms["edit-reponse"].fields.keys()) == [
        "objet",
        "reponse",
        "affectation",
        "comments",
        "submit",
    ]
    assert resp.forms.get("prefill-reponse") is None


def test_get_reponse_edit_form_not_found(app, lecture_an, amendements_an):
    resp = app.get(
        "http://localhost/lectures/an.15.269.PO717460/amendements/998/reponse",
        expect_errors=True,
    )
    assert resp.status_code == 404


def test_post_reponse_edit_form(app, lecture_an, amendements_an):
    from zam_repondeur.models import Amendement, DBSession

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.user_content.avis is None
    assert amendement.user_content.objet is None
    assert amendement.user_content.reponse is None
    initial_amendement_modified_at = amendement.modified_at

    resp = app.get(
        "http://localhost/lectures/an.15.269.PO717460/amendements/999/reponse"
    )
    form = resp.forms["edit-reponse"]
    form["avis"] = "Favorable"
    form["objet"] = "Un objet très pertinent"
    form["reponse"] = "Une réponse <strong>très</strong> appropriée"
    form["affectation"] = "6B"
    form["comments"] = "Avec des <table><tr><td>commentaires</td></tr></table>"
    resp = form.submit()

    assert resp.status_code == 302
    assert (
        resp.location
        == "http://localhost/lectures/an.15.269.PO717460/amendements/#amdt-999"
    )

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.user_content.avis == "Favorable"
    assert amendement.user_content.objet == "Un objet très pertinent"
    assert (
        amendement.user_content.reponse
        == "Une réponse <strong>très</strong> appropriée"
    )
    assert amendement.user_content.affectation == "6B"
    assert (
        amendement.user_content.comments
        == "Avec des <table><tbody><tr><td>commentaires</td></tr></tbody></table>"
    )
    assert initial_amendement_modified_at < amendement.modified_at


def test_post_reponse_edit_form_gouvernemental(app, lecture_an, amendements_an):
    from zam_repondeur.models import Amendement, DBSession

    amendement = amendements_an[1]
    with transaction.manager:
        amendement.auteur = "LE GOUVERNEMENT"
        DBSession.add(amendement)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.user_content.avis is None
    assert amendement.user_content.objet is None
    assert amendement.user_content.reponse is None
    assert amendement.gouvernemental
    initial_amendement_modified_at = amendement.modified_at

    resp = app.get(
        "http://localhost/lectures/an.15.269.PO717460/amendements/999/reponse"
    )
    form = resp.forms["edit-reponse"]
    form["reponse"] = "Une réponse <strong>très</strong> appropriée"
    form["comments"] = "Avec des <table><tr><td>commentaires</td></tr></table>"
    resp = form.submit()

    assert resp.status_code == 302
    assert (
        resp.location
        == "http://localhost/lectures/an.15.269.PO717460/amendements/#amdt-999"
    )

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.user_content.avis == ""
    assert amendement.user_content.objet == ""
    assert (
        amendement.user_content.reponse
        == "Une réponse <strong>très</strong> appropriée"
    )
    assert (
        amendement.user_content.comments
        == "Avec des <table><tbody><tr><td>commentaires</td></tr></tbody></table>"
    )
    assert initial_amendement_modified_at < amendement.modified_at


def test_post_reponse_edit_form_updates_modification_dates_only_if_modified(
    app, lecture_an, amendements_an
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

    # Let's post the response edit form, but with unchanged values
    resp = app.get(
        "http://localhost/lectures/an.15.269.PO717460/amendements/666/reponse"
    )
    form = resp.forms["edit-reponse"]
    form["avis"] = "Favorable"
    form["objet"] = "Un objet très pertinent"
    form["reponse"] = "Une réponse très appropriée"
    form.submit()

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
