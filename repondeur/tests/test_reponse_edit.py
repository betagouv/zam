import transaction


def test_get_reponse_edit_form(app, lecture_an, amendements_an):
    resp = app.get(
        "http://localhost/lectures/an.15.269.PO717460/amendements/999/reponse"
    )

    assert resp.status_code == 200
    assert resp.content_type == "text/html"
    assert resp.forms["edit-reponse"].method == "POST"


def test_get_reponse_edit_form_not_found(app, lecture_an, amendements_an):
    resp = app.get(
        "http://localhost/lectures/an.15.269.PO717460/amendements/998/reponse",
        expect_errors=True,
    )
    assert resp.status_code == 404


def test_post_reponse_edit_form(app, lecture_an, amendements_an):

    from zam_repondeur.models import Amendement, DBSession

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.avis is None
    assert amendement.observations is None
    assert amendement.reponse is None

    resp = app.get(
        "http://localhost/lectures/an.15.269.PO717460/amendements/999/reponse"
    )
    form = resp.forms["edit-reponse"]
    form["avis"] = "Favorable"
    form["observations"] = "Des observations très pertinentes"
    form["reponse"] = "Une réponse <strong>très</strong> appropriée"
    form["comments"] = "Avec des <table><tr><td>commentaires</td></tr></table>"
    resp = form.submit()

    assert resp.status_code == 302
    assert (
        resp.location
        == "http://localhost/lectures/an.15.269.PO717460/amendements/#amdt-999"
    )

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.avis == "Favorable"
    assert amendement.observations == "Des observations très pertinentes"
    assert amendement.reponse == "Une réponse <strong>très</strong> appropriée"
    assert (
        amendement.comments
        == "Avec des <table><tbody><tr><td>commentaires</td></tr></tbody></table>"
    )


def test_post_reponse_edit_form_updates_modification_date(
    app, lecture_an, amendements_an
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        initial_modified_at = lecture_an.modified_at

    resp = app.get(
        "http://localhost/lectures/an.15.269.PO717460/amendements/999/reponse"
    )
    form = resp.forms["edit-reponse"]
    form["avis"] = "Favorable"
    form["observations"] = "Des observations très pertinentes"
    form["reponse"] = "Une réponse très appropriée"
    form.submit()

    with transaction.manager:
        lecture = Lecture.get(
            chambre=lecture_an.chambre,
            session=lecture_an.session,
            num_texte=lecture_an.num_texte,
            organe=lecture_an.organe,
        )
        assert lecture.modified_at != initial_modified_at
