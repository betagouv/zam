def test_post_article_edit_form_title(app, lecture_an, amendements_an):
    from zam_repondeur.models.events.article import TitreArticleModifie
    from zam_repondeur.models import Amendement, DBSession

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()

    resp = app.get(
        "/lectures/an.15.269.PO717460/articles/article.1../", user="user@example.com"
    )
    form = resp.forms["edit-article"]
    form["title"] = "Titre article"
    resp = form.submit()

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()

    assert len(amendement.article.events) == 1
    event = amendement.article.events[0]
    assert isinstance(event, TitreArticleModifie)
    assert event.created_at is not None
    assert event.user.email == "user@example.com"
    assert event.data["old_value"] == ""
    assert event.data["new_value"] == "Titre article"
    assert (
        event.render_summary()
        == "<abbr title='user@example.com'>user@example.com</abbr> a modifié le titre"
    )
    assert event.render_details() == "De <del>«  »</del> à <ins>« Titre article »</ins>"


def test_post_article_edit_form_presentation(app, lecture_an, amendements_an):
    from zam_repondeur.models.events.article import PresentationArticleModifiee
    from zam_repondeur.models import Amendement, DBSession

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()

    resp = app.get(
        "/lectures/an.15.269.PO717460/articles/article.1../", user="user@example.com"
    )
    form = resp.forms["edit-article"]
    form["presentation"] = "<p>Content</p>"
    resp = form.submit()

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()

    assert len(amendement.article.events) == 1
    event = amendement.article.events[0]
    assert isinstance(event, PresentationArticleModifiee)
    assert event.created_at is not None
    assert event.user.email == "user@example.com"
    assert event.data["old_value"] == ""
    assert event.data["new_value"] == "<p>Content</p>"
    assert event.render_summary() == (
        "<abbr title='user@example.com'>user@example.com</abbr> a modifié "
        "la présentation"
    )
    assert event.render_details() == "De <del>«  »</del> à <ins>« Content »</ins>"
