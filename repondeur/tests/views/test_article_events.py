import transaction


def test_post_article_edit_form_title(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models.events.article import TitreArticleModifie
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        DBSession.add(user_david)

    amendement = DBSession.query(Amendement).filter(Amendement.num == "999").one()

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/articles/article.1../",
        user=user_david,
    )
    form = resp.forms["edit-article"]
    form["title"] = "Titre article"
    resp = form.submit()

    amendement = DBSession.query(Amendement).filter(Amendement.num == "999").one()

    assert len(amendement.article.events) == 1
    event = amendement.article.events[0]
    assert isinstance(event, TitreArticleModifie)
    assert event.created_at is not None
    assert event.user.email == "david@exemple.gouv.fr"
    assert event.data["old_value"] == ""
    assert event.data["new_value"] == "Titre article"
    assert event.render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> a ajouté le titre."
    )
    assert event.render_details() == "<ins>Titre article</ins> <del></del>"


def test_post_article_edit_form_presentation(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models.events.article import PresentationArticleModifiee
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        DBSession.add(user_david)

    amendement = DBSession.query(Amendement).filter(Amendement.num == "999").one()

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/articles/article.1../",
        user=user_david,
    )
    form = resp.forms["edit-article"]
    form["presentation"] = "<p>Content</p>"
    resp = form.submit()

    amendement = DBSession.query(Amendement).filter(Amendement.num == "999").one()

    assert len(amendement.article.events) == 1
    event = amendement.article.events[0]
    assert isinstance(event, PresentationArticleModifiee)
    assert event.created_at is not None
    assert event.user.email == "david@exemple.gouv.fr"
    assert event.data["old_value"] == ""
    assert event.data["new_value"] == "<p>Content</p>"
    assert event.render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> a ajouté la présentation."
    )
    assert event.render_details() == "<p><ins>Content</ins></p> <del></del>"
