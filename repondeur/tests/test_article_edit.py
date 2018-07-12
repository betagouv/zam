def test_get_article_edit_form(app, dummy_lecture, dummy_amendements):
    resp = app.get("http://localhost/lectures/an.15.269.PO717460/articles/article.1..")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"
    assert resp.forms["edit-article-title"].method == "post"


def test_post_article_edit_form(app, dummy_lecture, dummy_amendements):

    from zam_repondeur.models import Amendement, DBSession

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.subdiv_titre == ""

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/articles/article.1..")
    form = resp.forms["edit-article-title"]
    form["subdiv_titre"] = "Titre article"
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.subdiv_titre == "Titre article"
