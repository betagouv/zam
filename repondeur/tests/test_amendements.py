import transaction
from datetime import datetime


def test_get_amendements(app, lecture_an, amendements_an):
    resp = app.get("http://localhost/lectures/an.15.269.PO717460/amendements")
    assert resp.status_code == 200
    assert "Visualiser le dossier de banc" not in resp.text
    assert (
        "Vous devez saisir des réponses pour pouvoir visualiser le dossier de banc."
        in resp.text
    )


def test_get_amendements_with_avis(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendement = amendements_an[0]
        amendement.avis = "Favorable"

        # The object is no longer bound to a session here, as it was created in a
        # previous transaction, so we add it to the current session to make sure that
        # our changes will be committed with the current transaction
        DBSession.add(amendement)

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/amendements")
    assert resp.status_code == 200
    assert "Visualiser le dossier de banc" in resp.text


def test_get_amendements_with_gouvernemental(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendement = amendements_an[0]
        amendement.auteur = "LE GOUVERNEMENT"

        # The object is no longer bound to a session here, as it was created in a
        # previous transaction, so we add it to the current session to make sure that
        # our changes will be committed with the current transaction
        DBSession.add(amendement)

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/amendements")
    assert resp.status_code == 200
    assert "Visualiser le dossier de banc" in resp.text


def test_get_form(app, lecture_an, amendements_an):
    resp = app.get("/lectures/an.15.269.PO717460/amendements/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    assert resp.forms["amendement-666"].method == "post"
    assert (
        resp.forms["amendement-666"].action
        == "http://localhost/lectures/an.15.269.PO717460/amendements/666/"
    )

    assert list(resp.forms["amendement-666"].fields.keys()) == ["bookmark", "submit"]


def test_post_form_set(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession, Amendement

    assert amendements_an[0].bookmarked_at is None

    form = app.get("/lectures/an.15.269.PO717460/amendements/").forms["amendement-666"]
    form["bookmark"] = "1"

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    resp = resp.follow()

    assert resp.status_code == 200

    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.bookmarked_at


def test_post_form_unset(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession, Amendement

    with transaction.manager:
        amendements_an[0].bookmarked_at = datetime.now()
        DBSession.add(amendements_an[0])

    form = app.get("/lectures/an.15.269.PO717460/amendements/").forms["amendement-666"]
    form["bookmark"] = "0"

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    resp = resp.follow()

    assert resp.status_code == 200

    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.bookmarked_at is None


def test_post_form_set_then_unset(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession, Amendement

    assert amendements_an[0].bookmarked_at is None

    form = app.get("/lectures/an.15.269.PO717460/amendements/").forms["amendement-666"]
    form["bookmark"] = "1"

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    resp = resp.follow()

    assert resp.status_code == 200

    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.bookmarked_at

    form["bookmark"] = "0"

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    resp = resp.follow()

    assert resp.status_code == 200

    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.bookmarked_at is None


def test_get_amendements_not_found_bad_format(app):
    resp = app.get(
        "http://localhost/lectures/senat.2017-2018.1/amendements", expect_errors=True
    )
    assert resp.status_code == 404


def test_get_amendements_not_found_does_not_exist(app):
    resp = app.get(
        "http://localhost/lectures/an.15.269.PO717461/amendements", expect_errors=True
    )
    assert resp.status_code == 404
