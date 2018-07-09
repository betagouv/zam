import transaction


def test_reponses_empty(app, dummy_lecture, dummy_amendements):

    resp = app.get("http://localhost/lectures/an/15/269/PO717460/reponses")

    assert resp.status_code == 200
    assert resp.parser.tags("h1")[0].text() == str(dummy_lecture)
    assert len(resp.parser.tags("section")) == 0
    assert len(resp.parser.tags("article")) == 0


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
    assert resp.parser.tags("h1")[0].text() == str(dummy_lecture)
    assert len(resp.parser.tags("section")) == 1
    assert len(resp.parser.tags("article")) == 2
    assert len(resp.parser.css("article.gouvernemental")) == 0


def test_reponses_gouvernemental(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in dummy_amendements:
            amendement.auteur = "LE GOUVERNEMENT"
        DBSession.add_all(dummy_amendements)

    resp = app.get("http://localhost/lectures/an/15/269/PO717460/reponses")

    assert resp.parser.tags("h1")[0].text() == str(dummy_lecture)
    assert len(resp.parser.tags("section")) == 1
    assert len(resp.parser.tags("article")) == 2
    assert len(resp.parser.css("article.gouvernemental")) == 2


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

    assert len(resp.parser.tags("section")) == 2
    assert len(resp.parser.tags("article")) == 2
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

    assert len(resp.parser.tags("section")) == 2
    assert len(resp.parser.tags("article")) == 2
    assert len(resp.parser.css(".titles")) == 2
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

    assert len(resp.parser.tags("section")) == 2
    assert len(resp.parser.tags("article")) == 2
    assert len(resp.parser.css(".titles")) == 2
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

    assert resp.status_code == 200

    assert [section.attributes["id"] for section in resp.parser.tags("section")] == [
        "article-add-av-1",
        "article-1",
    ]
    assert len(resp.parser.tags("section")) == 2
    assert len(resp.parser.tags("article")) == 2
    assert len(resp.parser.css(".titles")) == 2
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

    assert resp.status_code == 200

    assert [section.attributes["id"] for section in resp.parser.tags("section")] == [
        "article-1",
        "article-add-ap-1",
    ]
    titles = [item.text() for item in resp.parser.css(".titles h2")]
    assert titles == ["Article 1", "Article add. ap. 1"]
