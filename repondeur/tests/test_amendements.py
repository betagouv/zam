import transaction
from datetime import datetime


def test_get_form(app, dummy_lecture, dummy_amendements):
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


def test_post_form_set(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession, Amendement

    assert dummy_amendements[0].bookmarked_at is None

    form = app.get("/lectures/an.15.269.PO717460/amendements/").forms["amendement-666"]
    form["bookmark"] = "1"

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    resp = resp.follow()

    assert resp.status_code == 200

    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.bookmarked_at


def test_post_form_unset(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession, Amendement

    with transaction.manager:
        dummy_amendements[0].bookmarked_at = datetime.now()
        DBSession.add(dummy_amendements[0])

    form = app.get("/lectures/an.15.269.PO717460/amendements/").forms["amendement-666"]
    form["bookmark"] = "0"

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    resp = resp.follow()

    assert resp.status_code == 200

    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.bookmarked_at is None


def test_post_form_set_then_unset(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession, Amendement

    assert dummy_amendements[0].bookmarked_at is None

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
