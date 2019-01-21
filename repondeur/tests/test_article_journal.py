import transaction


def first_details_text(resp):
    return (
        resp.parser.css_first(".timeline li details")
        .text()
        .strip()
        .split("\n")[-1]
        .strip()
    )


def first_summary_text(resp):
    return resp.parser.css_first(".timeline li details summary").text()


def test_article_journal_title(app, lecture_an, article1_an, user_david):
    from zam_repondeur.models.events.article import TitreArticleModifie

    with transaction.manager:
        TitreArticleModifie.create(
            request=None, article=article1_an, title="Title", user=user_david
        )
        assert len(article1_an.events) == 1
        assert article1_an.events[0].data["old_value"] == ""
        assert article1_an.events[0].data["new_value"] == "Title"

    resp = app.get(
        "/lectures/an.15.269.PO717460/articles/article.1../article_journal",
        user=user_david.email,
    )
    assert first_summary_text(resp) == "David a modifié le titre"
    assert first_details_text(resp) == "De «  » à « Title »"


def test_article_journal_title_from_services(app, lecture_an, article1_an):
    from zam_repondeur.models.events.article import TitreArticleModifie

    with transaction.manager:
        TitreArticleModifie.create(request=None, article=article1_an, title="Title")
        assert len(article1_an.events) == 1
        assert article1_an.events[0].data["old_value"] == ""
        assert article1_an.events[0].data["new_value"] == "Title"

    resp = app.get(
        "/lectures/an.15.269.PO717460/articles/article.1../article_journal",
        user="user@example.com",
    )
    assert first_summary_text(resp) == (
        "Le titre de l’article a été modifié par les services "
        "de l’Asssemblée nationale"
    )
    assert first_details_text(resp) == "De «  » à « Title »"


def test_article_journal_presentation(app, lecture_an, article1_an, user_david):
    from zam_repondeur.models.events.article import PresentationArticleModifiee

    with transaction.manager:
        PresentationArticleModifiee.create(
            request=None,
            article=article1_an,
            presentation="Présentation",
            user=user_david,
        )
        assert len(article1_an.events) == 1
        assert article1_an.events[0].data["old_value"] == ""
        assert article1_an.events[0].data["new_value"] == "Présentation"

    resp = app.get(
        "/lectures/an.15.269.PO717460/articles/article.1../article_journal",
        user=user_david.email,
    )
    assert first_summary_text(resp) == "David a modifié la présentation"
    assert first_details_text(resp) == "De «  » à « Présentation »"


def test_article_journal_content(app, lecture_an, article1_an, user_david):
    from zam_repondeur.models.events.article import ContenuArticleModifie

    with transaction.manager:
        ContenuArticleModifie.create(
            request=None, article=article1_an, content={"Foo": "Bar"}, user=user_david
        )
        assert len(article1_an.events) == 1
        assert article1_an.events[0].data["old_value"] == {}
        assert article1_an.events[0].data["new_value"] == {"Foo": "Bar"}

    resp = app.get(
        "/lectures/an.15.269.PO717460/articles/article.1../article_journal",
        user=user_david.email,
    )
    assert first_summary_text(resp) == (
        "Le contenu de l’article a été modifié par les services "
        "de l’Asssemblée nationale"
    )
