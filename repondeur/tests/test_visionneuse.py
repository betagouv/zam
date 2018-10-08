import transaction

import pytest


LECTURE_AN_URL = "http://localhost/lectures/an.15.269.PO717460"


def test_reponses_empty(app, lecture_an, amendements_an):

    resp = app.get(f"{LECTURE_AN_URL}/articles/article.1../reponses")

    assert resp.status_code == 200
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

    resp = app.get(f"{LECTURE_AN_URL}/articles/article.1../reponses")

    assert resp.status_code == 200
    test_amendement_666 = resp.find_amendement(amendements_an[0])
    assert test_amendement_666 is not None
    assert test_amendement_666.number_is_in_title()
    assert not test_amendement_666.has_gouvernemental_class()

    test_amendement_999 = resp.find_amendement(amendements_an[1])
    assert test_amendement_999 is not None
    assert test_amendement_999.number_is_in_title()
    assert not test_amendement_999.has_gouvernemental_class()

    assert (
        test_amendement_666.node.css_first("header h2").text().strip()
        != test_amendement_999.node.css_first("header h2").text().strip()
    )


def test_reponses_grouping(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations"
            amendement.reponse = f"Réponse"
        DBSession.add_all(amendements_an)

    resp = app.get(f"{LECTURE_AN_URL}/articles/article.1../reponses")

    assert resp.status_code == 200
    test_amendement_666 = resp.find_amendement(amendements_an[0])
    assert test_amendement_666.number_is_in_title()

    test_amendement_999 = resp.find_amendement(amendements_an[1])
    assert test_amendement_999.number_is_in_title()

    assert (
        test_amendement_666.node.css_first("header h2").text().strip()
        == test_amendement_999.node.css_first("header h2").text().strip()
    )


def test_reponses_not_grouping_on_same_reponse_only(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse"
        DBSession.add_all(amendements_an)

    resp = app.get(f"{LECTURE_AN_URL}/articles/article.1../reponses")

    assert resp.status_code == 200
    test_amendement_666 = resp.find_amendement(amendements_an[0])
    assert test_amendement_666.number_is_in_title()

    test_amendement_999 = resp.find_amendement(amendements_an[1])
    assert test_amendement_999.number_is_in_title()

    assert (
        test_amendement_666.node.css_first("header h2").text().strip()
        != test_amendement_999.node.css_first("header h2").text().strip()
    )


def test_reponses_gouvernemental(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.auteur = "LE GOUVERNEMENT"
        DBSession.add_all(amendements_an)

    resp = app.get(f"{LECTURE_AN_URL}/articles/article.1../reponses")

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

    resp = app.get(f"{LECTURE_AN_URL}/articles/article.1../reponses")

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

    resp = app.get(f"{LECTURE_AN_URL}/articles/article.1../reponses")

    test_amendement = resp.find_amendement(amendements_an[0])
    assert test_amendement is not None
    assert test_amendement.number_is_in_title()
    assert test_amendement.has_gouvernemental_class()

    assert resp.find_amendement(amendements_an[1]) is None


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

    resp = app.get(f"{LECTURE_AN_URL}/articles/article.1../reponses")

    fake_anchor = resp.parser.css_first("#content-article-1")
    article_content = fake_anchor.parent.css_first(".article")
    assert article_content.css_first("dt").text() == "001"
    assert article_content.css_first("dd").text().strip() == "Premier paragraphe"


def test_reponses_with_jaunes(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
            amendement.article.jaune = "<p>Contenu du jaune</p>"
        DBSession.add_all(amendements_an)

    resp = app.get(f"{LECTURE_AN_URL}/articles/article.1../reponses")

    fake_anchor = resp.parser.css_first("#content-article-1")
    article_content = fake_anchor.parent.css_first(".article")
    assert article_content.css_first("h2").text() == "Présentation de l’article"
    assert article_content.css_first("p").text().strip() == "Contenu du jaune"


def test_reponses_without_textes_or_jaunes(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
        DBSession.add_all(amendements_an)

    resp = app.get(f"{LECTURE_AN_URL}/articles/article.1../reponses")

    fake_anchor = resp.parser.css_first("#content-article-1")
    article_content = fake_anchor.parent.css_first(".article")
    assert article_content.css_first("h2") is None


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

    resp = app.get(f"{LECTURE_AN_URL}/articles/article.1../reponses")

    assert resp.parser.css(".titles h2")[0].text() == "Article 1"

    resp = app.get(f"{LECTURE_AN_URL}/articles/article.7.bis./reponses")

    assert resp.parser.css(".titles h2")[0].text() == "Article 7 bis"


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

    resp = app.get(f"{LECTURE_AN_URL}/articles/annexe.../reponses")

    assert resp.parser.css(".titles h2")[0].text() == "Annexes"


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

    resp = app.get(f"{LECTURE_AN_URL}/articles/article.1..avant/reponses")

    section_ids = [
        section.attributes.get("id")
        for section in resp.parser.tags("section")
        if "id" in section.attributes
    ]
    assert section_ids == ["article-add-av-1"]
    article_titles = [item.text() for item in resp.parser.css(".titles h2")]
    assert article_titles == ["Article add. av. 1"]


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

    resp = app.get(f"{LECTURE_AN_URL}/articles/article.1../reponses")

    assert "666" in resp
    assert "999 rect." in resp


def test_links_to_previous_and_next_articles(
    app, lecture_an, amendements_an, article1av_an, article7bis_an
):

    resp = app.get(f"{LECTURE_AN_URL}/articles/article.1../reponses")

    assert resp.status_code == 200
    nav_links = [node.text() for node in resp.parser.css(".secondary a")]
    assert nav_links == ["Article add. av. 1", "Article 7 bis"]
