import transaction


def test_get_reponse_edit_form(app, dummy_lecture, dummy_amendements):
    resp = app.get(
        "http://localhost/lectures/an/15/269/PO717460/amendements/999/reponse"
    )

    assert resp.status_code == 200
    assert resp.content_type == "text/html"
    assert resp.forms["edit-reponse"].method == "POST"


def test_post_reponse_edit_form(app, dummy_lecture, dummy_amendements):

    from zam_repondeur.models import Amendement, DBSession

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.avis is None
    assert amendement.observations is None
    assert amendement.reponse is None

    resp = app.get(
        "http://localhost/lectures/an/15/269/PO717460/amendements/999/reponse"
    )
    form = resp.forms["edit-reponse"]
    form["avis"] = "Favorable"
    form["observations"] = "Des observations très pertinentes"
    form["reponse"] = "Une réponse très appropriée"
    resp = form.submit()

    assert resp.status_code == 302
    assert (
        resp.location == "http://localhost/lectures/an/15/269/PO717460/amendements/list"
    )

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.avis == "Favorable"
    assert amendement.observations == "Des observations très pertinentes"
    assert amendement.reponse == "Une réponse très appropriée"


def test_post_reponse_edit_form_updates_modification_date(
    app, dummy_lecture, dummy_amendements
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        initial_modified_at = dummy_lecture.modified_at

    resp = app.get(
        "http://localhost/lectures/an/15/269/PO717460/amendements/999/reponse"
    )
    form = resp.forms["edit-reponse"]
    form["avis"] = "Favorable"
    form["observations"] = "Des observations très pertinentes"
    form["reponse"] = "Une réponse très appropriée"
    form.submit()

    with transaction.manager:
        lecture = Lecture.get(
            chambre=dummy_lecture.chambre,
            session=dummy_lecture.session,
            num_texte=dummy_lecture.num_texte,
            organe=dummy_lecture.organe,
        )
        assert lecture.modified_at != initial_modified_at
