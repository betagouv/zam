def test_get_reponse_edit_form(app, dummy_lecture, dummy_amendements):
    resp = app.get("http://localhost/lectures/an/15/269/amendements/999/reponse")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"
    assert resp.form.method == "POST"


def test_post_reponse_edit_form(app, dummy_lecture, dummy_amendements):

    from zam_repondeur.models import Amendement, DBSession

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.avis is None
    assert amendement.observations is None
    assert amendement.reponse is None

    form = app.get("http://localhost/lectures/an/15/269/amendements/999/reponse").form
    form["avis"] = "Favorable"
    form["observations"] = "Des observations très pertinentes"
    form["reponse"] = "Une réponse très appropriée"
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an/15/269/amendements/list"

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.avis == "Favorable"
    assert amendement.observations == "Des observations très pertinentes"
    assert amendement.reponse == "Une réponse très appropriée"
