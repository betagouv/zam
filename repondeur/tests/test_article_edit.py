def test_get_article_edit_form(app, dummy_lecture, dummy_amendements):
    resp = app.get("http://localhost/lectures/an.15.269.PO717460/articles/article.1..")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"
    assert resp.forms["edit-article"].method == "post"


def test_get_article_edit_form_not_found_bad_format(app, dummy_lecture):
    resp = app.get(
        "http://localhost/lectures/an.15.269.PO717460/articles/foo", expect_errors=True
    )
    assert resp.status_code == 404


def test_post_article_edit_form_title(app, dummy_lecture, dummy_amendements):

    from zam_repondeur.models import Amendement, DBSession

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.subdiv_titre == ""

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/articles/article.1..")
    form = resp.forms["edit-article"]
    form["subdiv_titre"] = "Titre article"
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.subdiv_titre == "Titre article"


def test_post_article_edit_form_jaune(app, dummy_lecture, dummy_amendements):

    from zam_repondeur.models import Amendement, DBSession

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.subdiv_jaune == ""

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/articles/article.1..")
    form = resp.forms["edit-article"]
    form["subdiv_jaune"] = "<p>Content</p>"
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.subdiv_jaune == "<p>Content</p>"


def test_post_article_edit_form_jaune_cleaned(app, dummy_lecture, dummy_amendements):

    from zam_repondeur.models import Amendement, DBSession

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.subdiv_jaune == ""

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/articles/article.1..")
    form = resp.forms["edit-article"]
    form["subdiv_jaune"] = "<h1>Content</h1>"
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.subdiv_jaune == "Content"
