import transaction
from pyramid.testing import DummyRequest


def first_description_text(resp):
    return resp.parser.css_first(".timeline li .what").text().strip()


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
            article=article1_an,
            title="Title",
            request=DummyRequest(remote_addr="127.0.0.1", user=user_david),
        )
        assert len(article1_an.events) == 1
        assert article1_an.events[0].data["old_value"] == ""
        assert article1_an.events[0].data["new_value"] == "Title"

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/articles/article.1../journal",
        user=user_david,
    )
    assert first_summary_text(resp) == "David a ajouté le titre."
    assert first_details_text(resp) == "Title"


def test_article_journal_title_clean(app, lecture_an, article1_an, user_david):
    from zam_repondeur.models.events.article import TitreArticleModifie

    with transaction.manager:
        TitreArticleModifie.create(
            article=article1_an,
            title="<script>Title</script>",
            request=DummyRequest(remote_addr="127.0.0.1", user=user_david),
        )
        assert len(article1_an.events) == 1
        assert article1_an.events[0].data["old_value"] == ""
        assert article1_an.events[0].data["new_value"] == "<script>Title</script>"

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/articles/article.1../journal",
        user=user_david,
    )
    assert first_summary_text(resp) == "David a ajouté le titre."
    assert (
        resp.parser.css_first(".timeline li details p").html
        == "<p><ins>Title</ins> <del></del></p>"
    )


def test_article_journal_title_from_services(app, lecture_an, article1_an, user_david):
    from zam_repondeur.models.events.article import TitreArticleModifie

    with transaction.manager:
        TitreArticleModifie.create(article=article1_an, title="Title")
        assert len(article1_an.events) == 1
        assert article1_an.events[0].data["old_value"] == ""
        assert article1_an.events[0].data["new_value"] == "Title"

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/articles/article.1../journal",
        user=user_david,
    )
    assert first_summary_text(resp) == (
        "Le titre de l’article a été modifié par les services "
        "de l’Asssemblée nationale."
    )
    assert first_details_text(resp) == "Title"


def test_article_journal_presentation(app, lecture_an, article1_an, user_david):
    from zam_repondeur.models.events.article import PresentationArticleModifiee

    with transaction.manager:
        PresentationArticleModifiee.create(
            article=article1_an,
            presentation="Présentation",
            request=DummyRequest(remote_addr="127.0.0.1", user=user_david),
        )
        assert len(article1_an.events) == 1
        assert article1_an.events[0].data["old_value"] == ""
        assert article1_an.events[0].data["new_value"] == "Présentation"

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/articles/article.1../journal",
        user=user_david,
    )
    assert first_summary_text(resp) == "David a ajouté la présentation."
    assert first_details_text(resp) == "Présentation"


def test_article_journal_content(app, lecture_an, article1_an, user_david):
    from zam_repondeur.models.events.article import ContenuArticleModifie

    with transaction.manager:
        ContenuArticleModifie.create(article=article1_an, content={"Foo": "Bar"})
        assert len(article1_an.events) == 1
        assert article1_an.events[0].data["old_value"] == {}
        assert article1_an.events[0].data["new_value"] == {"Foo": "Bar"}

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/articles/article.1../journal",
        user=user_david,
    )
    assert first_description_text(resp) == (
        "Le contenu de l’article a été modifié par les services "
        "de l’Asssemblée nationale."
    )
