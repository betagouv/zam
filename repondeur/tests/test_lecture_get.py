import transaction


def test_get_lecture(app, lecture_an, amendements_an):
    resp = app.get("http://localhost/lectures/an.15.269.PO717460/")
    assert resp.status_code == 200
    assert "Visualiser les réponses" not in resp.text


def test_get_lecture_with_avis(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendement = amendements_an[0]
        amendement.avis = "Favorable"

        # The object is no longer bound to a session here, as it was created in a
        # previous transaction, so we add it to the current session to make sure that
        # our changes will be committed with the current transaction
        DBSession.add(amendement)

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/")
    assert resp.status_code == 200
    assert "Visualiser les réponses" in resp.text


def test_get_lecture_with_gouvernemental(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendement = amendements_an[0]
        amendement.auteur = "LE GOUVERNEMENT"

        # The object is no longer bound to a session here, as it was created in a
        # previous transaction, so we add it to the current session to make sure that
        # our changes will be committed with the current transaction
        DBSession.add(amendement)

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/")
    assert resp.status_code == 200
    assert "Visualiser les réponses" in resp.text


def test_get_lecture_not_found_bad_format(app):
    resp = app.get("http://localhost/lectures/senat.2017-2018.1/", expect_errors=True)
    assert resp.status_code == 404


def test_get_lecture_not_found_does_not_exist(app):
    resp = app.get("http://localhost/lectures/an.15.269.PO717461/", expect_errors=True)
    assert resp.status_code == 404
