import pytest
import transaction


def _text_from_node(node, selector):
    return " ".join(node.css_first(selector).text().strip().split())


def test_reponses_empty(app, lecture_an, amendements_an, user_david):

    resp = app.get(
        (
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/articles/article.1.."
            "/reponses"
        ),
        user=user_david,
    )

    assert resp.status_code == 200
    assert resp.first_element(".titles h2") == "Article 1"
    assert resp.find_amendement(amendements_an[0]) is None
    assert resp.find_amendement(amendements_an[1]) is None


def test_reponses_full(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.user_content.avis = "Favorable"
            amendement.user_content.objet = f"Objet pour {amendement.num}"
            amendement.user_content.reponse = f"Réponse pour {amendement.num}"
        DBSession.add_all(amendements_an)

    resp = app.get(
        (
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/articles/article.1.."
            "/reponses"
        ),
        user=user_david,
    )

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
    assert _text_from_node(test_amendement_666.node, "header h2") == "Amendement 666"


def test_reponses_grouping(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.user_content.avis = "Favorable"
            amendement.user_content.objet = "Objet"
            amendement.user_content.reponse = "Réponse"
        DBSession.add_all(amendements_an)

    resp = app.get(
        (
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/articles/article.1.."
            "/reponses"
        ),
        user=user_david,
    )

    assert resp.status_code == 200
    test_amendement_666 = resp.find_amendement(amendements_an[0])
    assert test_amendement_666.number_is_in_title()

    test_amendement_999 = resp.find_amendement(amendements_an[1])
    assert test_amendement_999.number_is_in_title()

    assert (
        test_amendement_666.node.css_first("header h2").text().strip()
        == test_amendement_999.node.css_first("header h2").text().strip()
    )
    assert (
        _text_from_node(test_amendement_666.node, "header h2")
        == "Amendements 666 et 999"
    )


def test_reponses_authors_not_grouping(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.user_content.avis = "Favorable"
            amendement.user_content.objet = "Objet"
            amendement.user_content.reponse = "Réponse"
            amendement.auteur = "M. JEAN"
            amendement.groupe = "Les Indépendants"
        amendement.auteur = "M. CLAUDE"
        amendement.groupe = "Les Mécontents"
        DBSession.add_all(amendements_an)

    resp = app.get(
        (
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/articles/article.1.."
            "/reponses"
        ),
        user=user_david,
    )

    assert resp.status_code == 200
    test_amendement_666 = resp.find_amendement(amendements_an[0])
    assert test_amendement_666.number_is_in_title()

    test_amendement_999 = resp.find_amendement(amendements_an[1])
    assert test_amendement_999.number_is_in_title()

    assert (
        _text_from_node(test_amendement_666.node, "header .authors")
        == "M. JEAN (Les Indépendants ), M. CLAUDE (Les Mécontents )"
    )


def test_reponses_authors_grouping(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.user_content.avis = "Favorable"
            amendement.user_content.objet = "Objet"
            amendement.user_content.reponse = "Réponse"
            amendement.auteur = "M. JEAN"
            amendement.groupe = "Les Indépendants"
        DBSession.add_all(amendements_an)

    resp = app.get(
        (
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/articles/article.1.."
            "/reponses"
        ),
        user=user_david,
    )

    assert resp.status_code == 200
    test_amendement_666 = resp.find_amendement(amendements_an[0])
    assert test_amendement_666.number_is_in_title()

    test_amendement_999 = resp.find_amendement(amendements_an[1])
    assert test_amendement_999.number_is_in_title()

    assert (
        _text_from_node(test_amendement_666.node, "header .authors")
        == "M. JEAN (Les Indépendants )"
    )


def test_reponses_groupe_grouping(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.user_content.avis = "Favorable"
            amendement.user_content.objet = "Objet"
            amendement.user_content.reponse = "Réponse"
            amendement.auteur = "M. JEAN"
            amendement.groupe = "Les Indépendants"
        amendement.auteur = "M. CLAUDE"  # Only the last one.
        DBSession.add_all(amendements_an)

    resp = app.get(
        (
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/articles/article.1.."
            "/reponses"
        ),
        user=user_david,
    )

    assert resp.status_code == 200
    test_amendement_666 = resp.find_amendement(amendements_an[0])
    assert test_amendement_666.number_is_in_title()

    test_amendement_999 = resp.find_amendement(amendements_an[1])
    assert test_amendement_999.number_is_in_title()

    assert (
        _text_from_node(test_amendement_666.node, "header .authors")
        == "M. CLAUDE et M. JEAN (Les Indépendants )"
    )


def test_reponses_many_grouping(
    app, lecture_an, article1_an, amendements_an, user_david
):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.user_content.avis = "Défavorable"
            amendement.user_content.objet = "Objet"
            amendement.user_content.reponse = "Réponse"
            amendement.auteur = "M. JEAN"
            amendement.groupe = "Les Indépendants"
        amendement.auteur = "M. CLAUDE"  # Only the last one.
        DBSession.add_all(amendements_an)
        Amendement.create(
            lecture=lecture_an,
            article=article1_an,
            num=42,
            position=3,
            auteur="M. DUPONT",
            groupe="RDSE",
            avis="Défavorable",
            objet="Objet",
            reponse="Réponse",
        )
        Amendement.create(
            lecture=lecture_an,
            article=article1_an,
            num=57,
            position=4,
            auteur="M. DURAND",
            groupe="Les Républicains",
            avis="Défavorable",
            objet="Objet",
            reponse="Réponse",
        )
        Amendement.create(
            lecture=lecture_an,
            article=article1_an,
            num=72,
            position=5,
            auteur="M. MARTIN",
            groupe="Les Républicains",
            avis="Défavorable",
            objet="Objet",
            reponse="Réponse",
        )
        Amendement.create(
            lecture=lecture_an,
            article=article1_an,
            num=83,
            position=6,
            auteur="M. MARTIN",
            groupe="Les Républicains",
            avis="Défavorable",
            objet="Objet",
            reponse="Réponse",
        )

    resp = app.get(
        (
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/articles/article.1.."
            "/reponses"
        ),
        user=user_david,
    )

    assert resp.status_code == 200
    test_amendement_666 = resp.find_amendement(amendements_an[0])
    assert test_amendement_666.number_is_in_title()

    test_amendement_999 = resp.find_amendement(amendements_an[1])
    assert test_amendement_999.number_is_in_title()

    assert (
        _text_from_node(test_amendement_666.node, "header h2")
        == "Amendements 666, 999, …, 57, 72 et 83 (6 au total)"
    )
    assert _text_from_node(test_amendement_666.node, "header .authors") == (
        "M. CLAUDE et M. JEAN (Les Indépendants ), "
        "M. DURAND et M. MARTIN (Les Républicains ), "
        "M. DUPONT (RDSE )"
    )


def test_reponses_not_grouping_on_same_reponse_only(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.user_content.avis = "Favorable"
            amendement.user_content.objet = f"Objet pour {amendement.num}"
            amendement.user_content.reponse = "Réponse"
        DBSession.add_all(amendements_an)

    resp = app.get(
        (
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/articles/article.1.."
            "/reponses"
        ),
        user=user_david,
    )

    assert resp.status_code == 200
    test_amendement_666 = resp.find_amendement(amendements_an[0])
    assert test_amendement_666.number_is_in_title()

    test_amendement_999 = resp.find_amendement(amendements_an[1])
    assert test_amendement_999.number_is_in_title()

    assert (
        test_amendement_666.node.css_first("header h2").text().strip()
        != test_amendement_999.node.css_first("header h2").text().strip()
    )


def test_reponses_gouvernemental(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.auteur = "LE GOUVERNEMENT"
        DBSession.add_all(amendements_an)

    resp = app.get(
        (
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/articles/article.1.."
            "/reponses"
        ),
        user=user_david,
    )

    test_amendement = resp.find_amendement(amendements_an[0])
    assert test_amendement is not None
    assert test_amendement.number_is_in_title()
    assert test_amendement.has_gouvernemental_class()

    test_amendement = resp.find_amendement(amendements_an[1])
    assert test_amendement is not None
    assert test_amendement.number_is_in_title()
    assert test_amendement.has_gouvernemental_class()


@pytest.mark.parametrize(
    "sort",
    ["retiré", "irrecevable", "Irrecevable art. 40 C", "tombé", "retiré avant séance"],
)
def test_reponses_abandoned_not_displayed(
    app, lecture_an, amendements_an, sort, user_david
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.user_content.avis = "Favorable"
            amendement.user_content.objet = f"Objet pour {amendement.num}"
            amendement.user_content.reponse = f"Réponse pour {amendement.num}"
        # Only the last one.
        amendement.sort = sort
        DBSession.add_all(amendements_an)

    resp = app.get(
        (
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/articles/article.1.."
            "/reponses"
        ),
        user=user_david,
    )

    test_amendement = resp.find_amendement(amendements_an[0])
    assert test_amendement is not None
    assert test_amendement.number_is_in_title()
    assert not test_amendement.has_gouvernemental_class()

    assert resp.find_amendement(amendements_an[1]) is None


@pytest.mark.parametrize(
    "sort",
    ["retiré", "irrecevable", "Irrecevable art. 40 C", "tombé", "retiré avant séance"],
)
def test_reponses_abandoned_and_gouvernemental_not_displayed(
    app, lecture_an, amendements_an, sort, user_david
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.user_content.avis = "Favorable"
            amendement.user_content.objet = f"Objet pour {amendement.num}"
            amendement.user_content.reponse = f"Réponse pour {amendement.num}"
            amendement.auteur = "LE GOUVERNEMENT"
        # Only the last one.
        amendement.sort = sort
        DBSession.add_all(amendements_an)

    resp = app.get(
        (
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/articles/article.1.."
            "/reponses"
        ),
        user=user_david,
    )

    test_amendement = resp.find_amendement(amendements_an[0])
    assert test_amendement is not None
    assert test_amendement.number_is_in_title()
    assert test_amendement.has_gouvernemental_class()

    assert resp.find_amendement(amendements_an[1]) is None


def test_reponses_with_textes(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.user_content.avis = "Favorable"
            amendement.user_content.objet = f"Objet pour {amendement.num}"
            amendement.user_content.reponse = f"Réponse pour {amendement.num}"
            amendement.article.user_content.title = "Titre article"
            amendement.article.content = {"001": "Premier paragraphe"}
        DBSession.add_all(amendements_an)

    resp = app.get(
        (
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/articles/article.1.."
            "/reponses"
        ),
        user=user_david,
    )

    fake_anchor = resp.parser.css_first("#content-article-1")
    article_content = fake_anchor.parent.css_first(".article")
    assert article_content.css_first("h2").text() == "Titre article"
    assert article_content.css_first("h3").text() == "Texte de l’article"
    assert article_content.css_first("dt").text() == "001"
    assert article_content.css_first("dd").text().strip() == "Premier paragraphe"


def test_reponses_with_presentations(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.user_content.avis = "Favorable"
            amendement.user_content.objet = f"Objet pour {amendement.num}"
            amendement.user_content.reponse = f"Réponse pour {amendement.num}"
            amendement.article.user_content.presentation = (
                "<p>Contenu de la présentation</p>"
            )
        DBSession.add_all(amendements_an)

    resp = app.get(
        (
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/articles/article.1.."
            "/reponses"
        ),
        user=user_david,
    )

    fake_anchor = resp.parser.css_first("#content-article-1")
    article_content = fake_anchor.parent.css_first(".article")
    assert article_content.css_first("h3").text() == "Présentation de l’article"
    assert article_content.css_first("p").text().strip() == "Contenu de la présentation"


def test_reponses_without_textes_or_presentations(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.user_content.avis = "Favorable"
            amendement.user_content.objet = f"Objet pour {amendement.num}"
            amendement.user_content.reponse = f"Réponse pour {amendement.num}"
        DBSession.add_all(amendements_an)

    resp = app.get(
        (
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/articles/article.1.."
            "/reponses"
        ),
        user=user_david,
    )

    fake_anchor = resp.parser.css_first("#content-article-1")
    article_content = fake_anchor.parent.css_first(".article")
    assert article_content.css_first("h3") is None


def test_reponses_with_different_articles(
    app, lecture_an, amendements_an, article7bis_an, user_david
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for index, amendement in enumerate(amendements_an, 1):
            amendement.user_content.avis = "Favorable"
            amendement.user_content.objet = f"Objet pour {amendement.num}"
            amendement.user_content.reponse = f"Réponse pour {amendement.num}"
            amendement.article.user_content.title = f"Titre article {index}"
        # Only the last one.
        amendement.article = article7bis_an
        DBSession.add_all(amendements_an)

    resp = app.get(
        (
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/articles/article.1.."
            "/reponses"
        ),
        user=user_david,
    )

    assert resp.parser.css(".titles h2")[0].text() == "Article 1"
    assert len(resp.parser.css("nav.secondary")) == 2
    assert (
        resp.parser.css_first("nav.secondary .arrow-right").text().strip()
        == "Article 7 bis"
    )
    assert (
        resp.parser.css_first("nav.secondary.bottom .arrow-right").text().strip()
        == "Article 7 bis"
    )

    resp = app.get(
        (
            "/dossiers/plfss-2018/lectures"
            "/an.15.269.PO717460/articles"
            "/article.7.bis."
            "/reponses"
        )
    )

    assert resp.parser.css(".titles h2")[0].text() == "Article 7 bis"
    assert (
        resp.parser.css_first("nav.secondary .arrow-left").text().strip() == "Article 1"
    )
    assert (
        resp.parser.css_first("nav.secondary.bottom .arrow-left").text().strip()
        == "Article 1"
    )


def test_reponses_with_annexes(app, lecture_an, amendements_an, annexe_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for index, amendement in enumerate(amendements_an, 1):
            amendement.user_content.avis = "Favorable"
            amendement.user_content.objet = f"Objet pour {amendement.num}"
            amendement.user_content.reponse = f"Réponse pour {amendement.num}"
            amendement.article.user_content.title = f"Titre article {index}"
        # Only the last one.
        amendement.article = annexe_an
        DBSession.add_all(amendements_an)

    resp = app.get(
        (
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/articles/annexe..."
            "/reponses"
        ),
        user=user_david,
    )

    assert resp.parser.css(".titles h2")[0].text() == "Annexes"


def test_reponses_article_additionnel_avant(
    app, lecture_an, amendements_an, article1av_an, user_david
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.user_content.avis = "Favorable"
            amendement.user_content.objet = f"Objet pour {amendement.num}"
            amendement.user_content.reponse = f"Réponse pour {amendement.num}"
        amendements_an[0].article = article1av_an
        DBSession.add_all(amendements_an)

    resp = app.get(
        (
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/articles/article.1..avant"
            "/reponses"
        ),
        user=user_david,
    )

    section_ids = [
        section.attributes.get("id")
        for section in resp.parser.tags("section")
        if "id" in section.attributes
    ]
    assert section_ids == ["article-add-av-1"]
    article_titles = [item.text() for item in resp.parser.css(".titles h2")]
    assert article_titles == ["Article add. av. 1"]


def test_reponses_amendement_rect(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.user_content.avis = "Favorable"
            amendement.user_content.objet = f"Objet pour {amendement.num}"
            amendement.user_content.reponse = f"Réponse pour {amendement.num}"
        # Only the last one.
        amendement.rectif = 1
        DBSession.add_all(amendements_an)

    resp = app.get(
        (
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/articles/article.1.."
            "/reponses"
        ),
        user=user_david,
    )

    assert "666" in resp
    assert "999 rect." in resp


def test_links_to_previous_and_next_articles(
    app, lecture_an, amendements_an, article1av_an, article7bis_an, user_david
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendements_an[0].article = article1av_an
        amendements_an[0].user_content.avis = "Favorable"
        DBSession.add_all(amendements_an)

    resp = app.get(
        (
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/articles/article.1.."
            "/reponses"
        ),
        user=user_david,
    )

    assert resp.status_code == 200
    nav_links = [node.text() for node in resp.parser.css(".secondary a")]
    assert nav_links == ["Article add. av. 1", "Article 7 bis"]


def test_links_to_previous_and_next_articles_when_empty_additional(
    app, lecture_an, amendements_an, article1av_an, article7bis_an, user_david
):
    resp = app.get(
        (
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/articles/article.1.."
            "/reponses"
        ),
        user=user_david,
    )

    assert resp.status_code == 200
    nav_links = [node.text() for node in resp.parser.css(".secondary a")]
    assert nav_links == ["Article 7 bis"]
