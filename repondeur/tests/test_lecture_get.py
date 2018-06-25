import transaction


def test_get_lecture(app, dummy_lecture, dummy_amendements):
    resp = app.get("http://localhost/lectures/an/15/269/")
    assert resp.status_code == 200
    assert "Visualiser les réponses" not in resp.text


def test_get_lecture_with_avis(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).one()
        amendement.avis = "Favorable"

    resp = app.get("http://localhost/lectures/an/15/269/")
    assert resp.status_code == 200
    assert "Visualiser les réponses" in resp.text


def test_get_lecture_with_gouvernemental(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).one()
        amendement.auteur = "LE GOUVERNEMENT"

    resp = app.get("http://localhost/lectures/an/15/269/")
    assert resp.status_code == 200
    assert "Visualiser les réponses" in resp.text


def test_get_lecture_not_found(app):
    resp = app.get("http://localhost/lectures/senat/2017-2018/1/", expect_errors=True)
    assert resp.status_code == 404
