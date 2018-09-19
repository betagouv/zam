import transaction

import pytest


def test_reponses_empty(app, lecture_an, amendements_an):

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/reponses")

    assert resp.status_code == 200
    assert resp.first_element("h1") == lecture_an.dossier_legislatif
    assert resp.first_element("h2") == str(lecture_an)
    assert resp.first_element(".titles h2") == "Article 1"
    assert resp.find_amendement(amendements_an[0]) is None
    assert resp.find_amendement(amendements_an[1]) is None


def test_reponses_full(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
        DBSession.add_all(amendements_an)

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/reponses")

    assert resp.status_code == 200
    assert resp.first_element("h1") == lecture_an.dossier_legislatif
    assert resp.first_element("h2") == str(lecture_an)

    test_amendement = resp.find_amendement(amendements_an[0])
    assert test_amendement is not None
    assert test_amendement.number_is_in_title()
    assert not test_amendement.has_gouvernemental_class()

    test_amendement = resp.find_amendement(amendements_an[1])
    assert test_amendement is not None
    assert test_amendement.number_is_in_title()
    assert not test_amendement.has_gouvernemental_class()


def test_reponses_gouvernemental(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.auteur = "LE GOUVERNEMENT"
        DBSession.add_all(amendements_an)

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/reponses")

    test_amendement = resp.find_amendement(amendements_an[0])
    assert test_amendement is not None
    assert test_amendement.number_is_in_title()
    assert test_amendement.has_gouvernemental_class()

    test_amendement = resp.find_amendement(amendements_an[1])
    assert test_amendement is not None
    assert test_amendement.number_is_in_title()
    assert test_amendement.has_gouvernemental_class()


@pytest.mark.parametrize("sort", ["retiré", "irrecevable", "tombé"])
def test_reponses_abandoned_not_displayed(app, lecture_an, amendements_an, sort):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
        # Only the last one.
        amendement.sort = sort
        DBSession.add_all(amendements_an)

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/reponses")

    test_amendement = resp.find_amendement(amendements_an[0])
    assert test_amendement is not None
    assert test_amendement.number_is_in_title()
    assert not test_amendement.has_gouvernemental_class()

    assert resp.find_amendement(amendements_an[1]) is None


@pytest.mark.parametrize("sort", ["retiré", "irrecevable", "tombé"])
def test_reponses_abandoned_and_gouvernemental_not_displayed(
    app, lecture_an, amendements_an, sort
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
            amendement.auteur = "LE GOUVERNEMENT"
        # Only the last one.
        amendement.sort = sort
        DBSession.add_all(amendements_an)

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/reponses")

    test_amendement = resp.find_amendement(amendements_an[0])
    assert test_amendement is not None
    assert test_amendement.number_is_in_title()
    assert test_amendement.has_gouvernemental_class()

    assert resp.find_amendement(amendements_an[1]) is None


def test_reponses_menu(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
        DBSession.add_all(amendements_an)

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/reponses")

    assert len(resp.parser.css(".menu a")) == 1
    assert resp.parser.css_first(".menu a").text() == "Art. 1"


def test_reponses_menu_with_textes(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
            amendement.article.titre = "Titre article"
        DBSession.add_all(amendements_an)

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/reponses")

    assert len(resp.parser.css(".menu p strong")) == 1
    assert resp.parser.css_first(".menu p strong").text() == "Titre article :"


def test_reponses_with_textes(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
            amendement.article.titre = "Titre article"
            amendement.article.contenu = {"001": "Premier paragraphe"}
        DBSession.add_all(amendements_an)

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/reponses")

    assert len(resp.parser.css("#content-article-1")) == 1
    assert resp.parser.css_first("#content-article-1 dt").text() == "001"
    assert (
        resp.parser.css_first("#content-article-1 dd").text().strip()
        == "Premier paragraphe"
    )


def test_reponses_with_jaunes(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
            amendement.article.jaune = "<p>Contenu du jaune</p>"
        DBSession.add_all(amendements_an)

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/reponses")

    assert len(resp.parser.css("#content-article-1")) == 1
    assert (
        resp.parser.css_first("#content-article-1 h2").text() == "Éléments de langage"
    )
    assert (
        resp.parser.css_first("#content-article-1 p").text().strip()
        == "Contenu du jaune"
    )


def test_reponses_without_textes_or_jaunes(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
        DBSession.add_all(amendements_an)

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/reponses")

    assert len(resp.parser.css("#content-article-1 h2")) == 0


def test_reponses_with_different_articles(
    app, lecture_an, amendements_an, article7bis_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for index, amendement in enumerate(amendements_an, 1):
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
            amendement.article.titre = f"Titre article {index}"
        # Only the last one.
        amendement.article = article7bis_an
        DBSession.add_all(amendements_an)

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/reponses")

    assert resp.parser.css(".titles h2")[0].text() == "Article 1"
    assert resp.parser.css(".titles h2")[1].text() == "Article 7 bis"


def test_reponses_with_annexes(app, lecture_an, amendements_an, annexe_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for index, amendement in enumerate(amendements_an, 1):
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
            amendement.article.titre = f"Titre article {index}"
        # Only the last one.
        amendement.article = annexe_an
        DBSession.add_all(amendements_an)

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/reponses")

    assert resp.parser.css(".titles h2")[0].text() == "Article 1"
    assert resp.parser.css(".titles h2")[1].text() == "Annexes"


def test_reponses_article_additionnel_avant(
    app, lecture_an, amendements_an, article1av_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
        amendements_an[0].article = article1av_an
        DBSession.add_all(amendements_an)

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/reponses")

    section_ids = [section.attributes["id"] for section in resp.parser.tags("section")]
    assert section_ids == ["article-add-av-1", "article-1"]
    article_titles = [item.text() for item in resp.parser.css(".titles h2")]
    assert article_titles == ["Article add. av. 1", "Article 1"]


def test_reponses_amendement_rect(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
        # Only the last one.
        amendement.rectif = 1
        DBSession.add_all(amendements_an)

    resp = app.get("http://localhost/lectures/an.15.269.PO717460/reponses")

    assert "666" in resp
    assert "999 rect." in resp
