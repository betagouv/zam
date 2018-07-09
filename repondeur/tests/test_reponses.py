import transaction

import pytest


def test_reponses_empty(app, dummy_lecture, dummy_amendements):

    resp = app.get("http://localhost/lectures/an/15/269/PO717460/reponses")

    assert resp.status_code == 200
    assert resp.first_h1 == str(dummy_lecture)
    assert resp.find_amendement(dummy_amendements[0]) is None
    assert resp.find_amendement(dummy_amendements[1]) is None


def test_reponses_full(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in dummy_amendements:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
        DBSession.add_all(dummy_amendements)

    resp = app.get("http://localhost/lectures/an/15/269/PO717460/reponses")

    assert resp.status_code == 200
    assert resp.first_h1 == str(dummy_lecture)

    test_amendement = resp.find_amendement(dummy_amendements[0])
    assert test_amendement is not None
    assert test_amendement.number_is_in_title()
    assert not test_amendement.has_gouvernemental_class()

    test_amendement = resp.find_amendement(dummy_amendements[1])
    assert test_amendement is not None
    assert test_amendement.number_is_in_title()
    assert not test_amendement.has_gouvernemental_class()


def test_reponses_gouvernemental(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in dummy_amendements:
            amendement.auteur = "LE GOUVERNEMENT"
        DBSession.add_all(dummy_amendements)

    resp = app.get("http://localhost/lectures/an/15/269/PO717460/reponses")

    assert resp.first_h1 == str(dummy_lecture)

    test_amendement = resp.find_amendement(dummy_amendements[0])
    assert test_amendement is not None
    assert test_amendement.number_is_in_title()
    assert test_amendement.has_gouvernemental_class()

    test_amendement = resp.find_amendement(dummy_amendements[1])
    assert test_amendement is not None
    assert test_amendement.number_is_in_title()
    assert test_amendement.has_gouvernemental_class()


@pytest.mark.parametrize("sort", ["retiré", "irrecevable", "tombé"])
def test_reponses_abandonned_not_displayed(app, dummy_lecture, dummy_amendements, sort):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in dummy_amendements:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
        # Only the last one.
        amendement.sort = sort
        DBSession.add_all(dummy_amendements)

    resp = app.get("http://localhost/lectures/an/15/269/PO717460/reponses")

    assert resp.first_h1 == str(dummy_lecture)

    test_amendement = resp.find_amendement(dummy_amendements[0])
    assert test_amendement is not None
    assert test_amendement.number_is_in_title()
    assert not test_amendement.has_gouvernemental_class()

    assert resp.find_amendement(dummy_amendements[1]) is None


@pytest.mark.parametrize("sort", ["retiré", "irrecevable", "tombé"])
def test_reponses_abandonned_and_gouvernemental_not_displayed(
    app, dummy_lecture, dummy_amendements, sort
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in dummy_amendements:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
            amendement.auteur = "LE GOUVERNEMENT"
        # Only the last one.
        amendement.sort = sort
        DBSession.add_all(dummy_amendements)

    resp = app.get("http://localhost/lectures/an/15/269/PO717460/reponses")

    assert resp.first_h1 == str(dummy_lecture)
    test_amendement = resp.find_amendement(dummy_amendements[0])
    assert test_amendement is not None
    assert test_amendement.number_is_in_title()
    assert test_amendement.has_gouvernemental_class()

    assert resp.find_amendement(dummy_amendements[1]) is None


def test_reponses_menu(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in dummy_amendements:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
        DBSession.add_all(dummy_amendements)

    resp = app.get("http://localhost/lectures/an/15/269/PO717460/reponses")

    assert len(resp.parser.css(".menu a")) == 1
    assert resp.parser.css_first(".menu a").text() == "Art. 1"


def test_reponses_menu_with_textes(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in dummy_amendements:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
            amendement.subdiv_titre = "Titre article"
        DBSession.add_all(dummy_amendements)

    resp = app.get("http://localhost/lectures/an/15/269/PO717460/reponses")

    assert len(resp.parser.css(".menu p strong")) == 1
    assert resp.parser.css_first(".menu p strong").text() == "Titre article :"


def test_reponses_with_textes(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in dummy_amendements:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
            amendement.subdiv_titre = "Titre article"
            amendement.subdiv_contenu = {"001": "Premier paragraphe"}
        DBSession.add_all(dummy_amendements)

    resp = app.get("http://localhost/lectures/an/15/269/PO717460/reponses")

    assert len(resp.parser.css("#content-article-1")) == 1
    assert resp.parser.css_first("#content-article-1 dt").text() == "001"
    assert (
        resp.parser.css_first("#content-article-1 dd").text().strip()
        == "Premier paragraphe"
    )


def test_reponses_without_textes(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in dummy_amendements:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
        DBSession.add_all(dummy_amendements)

    resp = app.get("http://localhost/lectures/an/15/269/PO717460/reponses")

    assert len(resp.parser.css("#content-article-1")) == 0


def test_reponses_with_multiple_articles(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for index, amendement in enumerate(dummy_amendements, 1):
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
            amendement.subdiv_titre = f"Titre article {index}"
        # Only the last one.
        amendement.subdiv_num = 2
        DBSession.add_all(dummy_amendements)

    resp = app.get("http://localhost/lectures/an/15/269/PO717460/reponses")

    assert len(resp.parser.css(".titles")) == 2
    for index, item in enumerate(resp.parser.css(".titles h2"), 1):
        assert item.text() == f"Article {index}"
    for index, item in enumerate(resp.parser.css(".titles h3"), 1):
        assert item.text() == f"Titre article {index}"
    assert len(resp.parser.css(".menu p strong")) == 2
    for index, item in enumerate(resp.parser.css(".menu p strong"), 1):
        assert item.text() == f"Titre article {index} :"


def test_reponses_with_multiplicatif_articles(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for index, amendement in enumerate(dummy_amendements, 1):
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
            amendement.subdiv_titre = f"Titre article {index}"
        # Only the last one.
        amendement.subdiv_mult = "bis"
        DBSession.add_all(dummy_amendements)

    resp = app.get("http://localhost/lectures/an/15/269/PO717460/reponses")

    assert resp.parser.css(".titles h2")[0].text() == "Article 1"
    assert resp.parser.css(".titles h2")[1].text() == "Article 1 bis"


def test_reponses_with_annexes(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for index, amendement in enumerate(dummy_amendements, 1):
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
            amendement.subdiv_titre = f"Titre article {index}"
        # Only the last one.
        amendement.subdiv_num = ""
        amendement.subdiv_type = "annexe"
        DBSession.add_all(dummy_amendements)

    resp = app.get("http://localhost/lectures/an/15/269/PO717460/reponses")

    assert resp.parser.css(".titles h2")[0].text() == "Article 1"
    assert resp.parser.css(".titles h2")[1].text() == "Annexes"


def test_reponses_article_additionnel_avant(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in dummy_amendements:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
        dummy_amendements[0].subdiv_pos = "avant"
        DBSession.add_all(dummy_amendements)

    resp = app.get("http://localhost/lectures/an/15/269/PO717460/reponses")

    section_ids = [section.attributes["id"] for section in resp.parser.tags("section")]
    assert section_ids == ["article-add-av-1", "article-1"]
    article_titles = [item.text() for item in resp.parser.css(".titles h2")]
    assert article_titles == ["Article add. av. 1", "Article 1"]


def test_reponses_article_additionnel_apres(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in dummy_amendements:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
        dummy_amendements[1].subdiv_pos = "après"
        DBSession.add_all(dummy_amendements)

    resp = app.get("http://localhost/lectures/an/15/269/PO717460/reponses")

    section_ids = [section.attributes["id"] for section in resp.parser.tags("section")]
    assert section_ids == ["article-1", "article-add-ap-1"]
    article_titles = [item.text() for item in resp.parser.css(".titles h2")]
    assert article_titles == ["Article 1", "Article add. ap. 1"]


def test_reponses_amendement_rect(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in dummy_amendements:
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
        # Only the last one.
        amendement.rectif = 1
        DBSession.add_all(dummy_amendements)

    resp = app.get("http://localhost/lectures/an/15/269/PO717460/reponses")

    assert "666" in resp
    assert "999 rect." in resp
