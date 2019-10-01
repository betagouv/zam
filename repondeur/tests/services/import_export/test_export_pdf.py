import pytest
import transaction
from pyramid.testing import DummyRequest
from selectolax.parser import HTMLParser


def _html_page_titles(parser, selector=".page header"):
    return [node.text().strip() for node in parser.css(selector)]


def _cartouche_to_list(response_node):
    return [
        " ".join(part.strip() for part in node.text().strip().split("\n"))
        for node in response_node.css("table.cartouche tr td")
        if node.text().strip()
    ]


def test_generate_pdf_without_responses(
    app, lecture_senat, article1_senat, article1av_senat, article7bis_senat
):
    from zam_repondeur.models import Amendement
    from zam_repondeur.services.import_export.pdf import generate_html_for_pdf

    amendement = Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=42,
        rectif=1,
        auteur="M. DUPONT",
        groupe="RDSE",
        matricule="000000",
        corps="<p>L'article 1 est supprimé.</p>",
        expose="<p>Cet article va à l'encontre du principe d'égalité.</p>",
        resume="Suppression de l'article",
        position=1,
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article1av_senat,
        alinea="",
        num=57,
        auteur="M. DURAND",
        groupe="Les Républicains",
        matricule="000001",
        corps="baz",
        expose="qux",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article7bis_senat,
        alinea="",
        num=21,
        auteur="M. MARTIN",
        groupe=None,
        matricule="000002",
        corps="quux",
        expose="quuz",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=43,
        auteur="M. JEAN",
        groupe="Les Indépendants",
        matricule="000003",
        corps="corge",
        expose="grault",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=596,
        rectif=1,
        parent=amendement,
        auteur="M. JEAN",
        groupe="Les Indépendants",
        matricule="000003",
        corps="corge",
        expose="grault",
    )

    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )

    assert parser.css_first("h1").text() == "Sécurité sociale : loi de financement 2018"
    assert (
        parser.css_first(".first-page .lecture").text()
        == "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063"
    )
    assert _html_page_titles(parser) == ["Article 1", "Article 7 bis"]


def test_generate_pdf_with_amendement_responses(
    app, lecture_senat, article1_senat, article1av_senat, article7bis_senat
):
    from zam_repondeur.models import Amendement
    from zam_repondeur.services.import_export.pdf import generate_html_for_pdf

    amendement = Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=42,
        rectif=1,
        auteur="M. DUPONT",
        groupe="RDSE",
        matricule="000000",
        corps="<p>L'article 1 est supprimé.</p>",
        expose="<p>Cet article va à l'encontre du principe d'égalité.</p>",
        resume="Suppression de l'article",
        position=1,
        avis="Favorable",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article1av_senat,
        alinea="",
        num=57,
        auteur="M. DURAND",
        groupe="Les Républicains",
        matricule="000001",
        corps="baz",
        expose="qux",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article7bis_senat,
        alinea="",
        num=21,
        auteur="M. MARTIN",
        groupe=None,
        matricule="000002",
        corps="quux",
        expose="quuz",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=43,
        auteur="M. JEAN",
        groupe="Les Indépendants",
        matricule="000003",
        corps="corge",
        expose="grault",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=596,
        rectif=1,
        parent=amendement,
        auteur="M. JEAN",
        groupe="Les Indépendants",
        matricule="000003",
        corps="corge",
        expose="grault",
    )

    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )

    assert (
        parser.css_first(".first-page .lecture").text()
        == "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063"
    )
    assert _html_page_titles(parser) == [
        "Article 1",
        "Réponse",
        "Amendement nº 42 rect.",
        "Article 7 bis",
    ]


def test_generate_pdf_with_amendement_content(
    app, lecture_senat, article1_senat, amendements_senat
):
    from zam_repondeur.models import DBSession
    from zam_repondeur.services.import_export.pdf import generate_html_for_pdf

    amendement_6666 = amendements_senat[0]
    amendement_6666.auteur = "M. JEAN"
    amendement_6666.groupe = "Les Indépendants"
    amendement_6666.user_content.avis = "Favorable"
    amendement_6666.user_content.objet = "L’objet"
    amendement_6666.user_content.reponse = "La réponse"
    DBSession.add(amendement_6666)

    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )

    assert (
        parser.css_first(".first-page .lecture").text()
        == "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063"
    )
    assert _html_page_titles(parser) == ["Article 1", "Réponse", "Amendement nº 6666"]
    response_node = parser.css_first(".reponse")
    assert _cartouche_to_list(response_node) == [
        "Article",
        "Art. 1",
        "Amendement",
        "6666",
        "Auteur",
        "M. JEAN",
        "Groupe",
        "Les Indépendants",
        "Avis",
        "Favorable",
    ]
    assert response_node.css_first("div h5").text() == "Objet"
    assert "L’objet" in response_node.css_first("div p").text()
    assert response_node.css("div h5")[-1].text() == "Réponse"
    assert "La réponse" in response_node.css("div p")[-1].text()


def test_generate_pdf_with_amendement_content_factor_authors_groups(
    app, lecture_senat, article1_senat, amendements_senat
):
    from zam_repondeur.models import DBSession
    from zam_repondeur.services.import_export.pdf import generate_html_for_pdf

    amendement_6666 = amendements_senat[0]
    amendement_6666.auteur = "M. JEAN"
    amendement_6666.groupe = "Les Indépendants"
    amendement_6666.user_content.avis = "Favorable"
    amendement_6666.user_content.objet = "L’objet"
    amendement_6666.user_content.reponse = "La réponse"
    DBSession.add(amendement_6666)

    amendement_9999 = amendements_senat[1]
    amendement_9999.auteur = "M. JEAN"
    amendement_9999.groupe = "Les Indépendants"
    amendement_9999.user_content.avis = "Favorable"
    amendement_9999.user_content.objet = "L’objet"
    amendement_9999.user_content.reponse = "La réponse"
    DBSession.add(amendement_9999)

    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )

    assert (
        parser.css_first(".first-page .lecture").text()
        == "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063"
    )
    assert _html_page_titles(parser) == [
        "Article 1",
        "Réponse",
        "Amendement nº 6666",
        "Amendement nº 9999",
    ]
    response_node = parser.css_first(".reponse")
    assert _cartouche_to_list(response_node) == [
        "Article",
        "Art. 1",
        "Amendements",
        "6666 et 9999",
        "Auteurs",
        "M. JEAN",
        "Groupes",
        "Les Indépendants",
        "Avis",
        "Favorable",
    ]
    assert response_node.css_first("div h5").text() == "Objet"
    assert "L’objet" in response_node.css_first("div p").text()
    assert response_node.css("div h5")[-1].text() == "Réponse"
    assert "La réponse" in response_node.css("div p")[-1].text()


def test_generate_pdf_with_amendement_content_factor_only_groups(
    app, lecture_senat, article1_senat, amendements_senat
):
    from zam_repondeur.models import DBSession
    from zam_repondeur.services.import_export.pdf import generate_html_for_pdf

    amendement_6666 = amendements_senat[0]
    amendement_6666.auteur = "M. JEAN"
    amendement_6666.groupe = "Les Indépendants"
    amendement_6666.user_content.avis = "Favorable"
    amendement_6666.user_content.objet = "L’objet"
    amendement_6666.user_content.reponse = "La réponse"
    DBSession.add(amendement_6666)

    amendement_9999 = amendements_senat[1]
    amendement_9999.auteur = "M. CLAUDE"
    amendement_9999.groupe = "Les Indépendants"
    amendement_9999.user_content.avis = "Favorable"
    amendement_9999.user_content.objet = "L’objet"
    amendement_9999.user_content.reponse = "La réponse"
    DBSession.add(amendement_9999)

    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )

    assert (
        parser.css_first(".first-page .lecture").text()
        == "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063"
    )
    assert _html_page_titles(parser) == [
        "Article 1",
        "Réponse",
        "Amendement nº 6666",
        "Amendement nº 9999",
    ]
    response_node = parser.css_first(".reponse")
    assert _cartouche_to_list(response_node) == [
        "Article",
        "Art. 1",
        "Amendements",
        "6666 et 9999",
        "Auteurs",
        "M. CLAUDE et M. JEAN",
        "Groupes",
        "Les Indépendants",
        "Avis",
        "Favorable",
    ]
    assert response_node.css_first("div h5").text() == "Objet"
    assert "L’objet" in response_node.css_first("div p").text()
    assert response_node.css("div h5")[-1].text() == "Réponse"
    assert "La réponse" in response_node.css("div p")[-1].text()


def test_generate_pdf_with_amendement_content_factor_many_authors_groups(
    app, lecture_senat, article1_senat, amendements_senat
):
    from zam_repondeur.models import Amendement, DBSession
    from zam_repondeur.services.import_export.pdf import generate_html_for_pdf

    amendement_6666 = amendements_senat[0]
    amendement_6666.auteur = "M. JEAN"
    amendement_6666.groupe = "Les Indépendants"
    amendement_6666.user_content.avis = "Défavorable"
    amendement_6666.user_content.objet = "L’objet"
    amendement_6666.user_content.reponse = "La réponse"
    DBSession.add(amendement_6666)

    amendement_9999 = amendements_senat[1]
    amendement_9999.auteur = "M. JEAN"
    amendement_9999.groupe = "Les Indépendants"
    amendement_9999.user_content.avis = "Défavorable"
    amendement_9999.user_content.objet = "L’objet"
    amendement_9999.user_content.reponse = "La réponse"
    DBSession.add(amendement_9999)

    Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        num=42,
        position=3,
        auteur="M. DUPONT",
        groupe="RDSE",
        avis="Défavorable",
        objet="L’objet",
        reponse="La réponse",
    )

    Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        num=57,
        position=4,
        auteur="M. DURAND",
        groupe="Les Républicains",
        avis="Défavorable",
        objet="L’objet",
        reponse="La réponse",
    )

    Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        num=72,
        position=5,
        auteur="M. MARTIN",
        groupe="Les Républicains",
        avis="Défavorable",
        objet="L’objet",
        reponse="La réponse",
    )

    Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        num=83,
        position=6,
        auteur="M. MARTIN",
        groupe="Les Républicains",
        avis="Défavorable",
        objet="L’objet",
        reponse="La réponse",
    )

    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )

    assert (
        parser.css_first(".first-page .lecture").text()
        == "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063"
    )
    assert _html_page_titles(parser) == [
        "Article 1",
        "Réponse",
        "Amendement nº 6666",
        "Amendement nº 9999",
        "Amendement nº 42",
        "Amendement nº 57",
        "Amendement nº 72",
        "Amendement nº 83",
    ]
    response_node = parser.css_first(".reponse")
    assert _cartouche_to_list(response_node) == [
        "Article",
        "Art. 1",
        "Amendements",
        "6666, 9999, …, 57, 72 et 83 (6 au total)",
        "Auteurs",
        "M. DUPONT, M. DURAND, M. JEAN et M. MARTIN",
        "Groupes",
        "Les Indépendants, Les Républicains et RDSE",
        "Avis",
        "Défavorable",
    ]
    assert response_node.css_first("div h5").text() == "Objet"
    assert "L’objet" in response_node.css_first("div p").text()
    assert response_node.css("div h5")[-1].text() == "Réponse"
    assert "La réponse" in response_node.css("div p")[-1].text()


def test_generate_pdf_with_amendement_content_gouvernemental(
    app, lecture_senat, article1_senat, amendements_senat
):
    from zam_repondeur.models import DBSession
    from zam_repondeur.services.import_export.pdf import generate_html_for_pdf

    amendement_6666 = amendements_senat[0]
    amendement_6666.auteur = "LE GOUVERNEMENT"
    amendement_6666.user_content.reponse = "La présentation"
    DBSession.add(amendement_6666)

    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )

    assert (
        parser.css_first(".first-page .lecture").text()
        == "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063"
    )
    assert _html_page_titles(parser) == ["Article 1", "Réponse", "Amendement nº 6666"]
    response_node = parser.css_first(".reponse")
    assert _cartouche_to_list(response_node) == [
        "Article",
        "Art. 1",
        "Amendement",
        "6666",
        "Auteur",
        "Gouvernement",
    ]
    assert response_node.css_first("div h5").text() == "Réponse"
    assert "La présentation" in response_node.css_first("div p").text()


def test_generate_pdf_with_amendement_and_sous_amendement_responses(
    app, lecture_senat, article1_senat, article1av_senat, article7bis_senat
):
    from zam_repondeur.models import Amendement
    from zam_repondeur.services.import_export.pdf import generate_html_for_pdf

    amendement = Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=42,
        rectif=1,
        auteur="M. DUPONT",
        groupe="RDSE",
        matricule="000000",
        corps="<p>L'article 1 est supprimé.</p>",
        expose="<p>Cet article va à l'encontre du principe d'égalité.</p>",
        resume="Suppression de l'article",
        position=1,
        avis="Favorable",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article1av_senat,
        alinea="",
        num=57,
        auteur="M. DURAND",
        groupe="Les Républicains",
        matricule="000001",
        corps="baz",
        expose="qux",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article7bis_senat,
        alinea="",
        num=21,
        auteur="M. MARTIN",
        groupe=None,
        matricule="000002",
        corps="quux",
        expose="quuz",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=43,
        auteur="M. JEAN",
        groupe="Les Indépendants",
        matricule="000003",
        corps="corge",
        expose="grault",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=596,
        rectif=1,
        parent=amendement,
        auteur="M. JEAN",
        groupe="Les Indépendants",
        matricule="000003",
        corps="corge",
        expose="grault",
        avis="Défavorable",
    )

    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )

    assert (
        parser.css_first(".first-page .lecture").text()
        == "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063"
    )
    assert _html_page_titles(parser) == [
        "Article 1",
        "Réponse",
        "Amendement nº 42 rect.",
        "Réponse",
        "Sous-amendement nº 596 rect.",
        "Article 7 bis",
    ]


def test_generate_pdf_with_additional_article_amendements_having_responses(
    app, lecture_senat, article1_senat, article1av_senat, article7bis_senat
):
    from zam_repondeur.models import Amendement
    from zam_repondeur.services.import_export.pdf import generate_html_for_pdf

    amendement = Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=42,
        rectif=1,
        auteur="M. DUPONT",
        groupe="RDSE",
        matricule="000000",
        corps="<p>L'article 1 est supprimé.</p>",
        expose="<p>Cet article va à l'encontre du principe d'égalité.</p>",
        resume="Suppression de l'article",
        position=1,
        avis="Favorable",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article1av_senat,
        alinea="",
        num=57,
        auteur="M. DURAND",
        groupe="Les Républicains",
        matricule="000001",
        corps="baz",
        expose="qux",
        avis="Favorable",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article7bis_senat,
        alinea="",
        num=21,
        auteur="M. MARTIN",
        groupe=None,
        matricule="000002",
        corps="quux",
        expose="quuz",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=43,
        auteur="M. JEAN",
        groupe="Les Indépendants",
        matricule="000003",
        corps="corge",
        expose="grault",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=596,
        rectif=1,
        parent=amendement,
        auteur="M. JEAN",
        groupe="Les Indépendants",
        matricule="000003",
        corps="corge",
        expose="grault",
    )

    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )

    assert (
        parser.css_first(".first-page .lecture").text()
        == "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063"
    )
    assert _html_page_titles(parser) == [
        "Réponse",
        "Amendement nº 57",
        "Article 1",
        "Réponse",
        "Amendement nº 42 rect.",
        "Article 7 bis",
    ]


def test_generate_pdf_amendement_without_responses(app, lecture_senat, article1_senat):
    from zam_repondeur.models import Amendement
    from zam_repondeur.services.import_export.pdf import generate_html_for_pdf

    amendement = Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=42,
        rectif=1,
        auteur="M. DUPONT",
        groupe="RDSE",
        matricule="000000",
        corps="<p>L'article 1 est supprimé.</p>",
        expose="<p>Cet article va à l'encontre du principe d'égalité.</p>",
        resume="Suppression de l'article",
        position=1,
    )

    parser = HTMLParser(
        generate_html_for_pdf(
            DummyRequest(), "print_multiple.html", {"amendements": [amendement]}
        )
    )

    assert _html_page_titles(parser) == ["Amendement nº 42 rect."]


def test_generate_pdf_amendement_with_responses(app, lecture_senat, article1_senat):
    from zam_repondeur.models import Amendement
    from zam_repondeur.services.import_export.pdf import generate_html_for_pdf

    amendement = Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=42,
        rectif=1,
        auteur="M. DUPONT",
        groupe="RDSE",
        matricule="000000",
        corps="<p>L'article 1 est supprimé.</p>",
        expose="<p>Cet article va à l'encontre du principe d'égalité.</p>",
        resume="Suppression de l'article",
        position=1,
        avis="Favorable",
    )

    parser = HTMLParser(
        generate_html_for_pdf(
            DummyRequest(), "print_multiple.html", {"amendements": [amendement]}
        )
    )

    assert _html_page_titles(parser) == ["Réponse", "Amendement nº 42 rect."]


def test_generate_pdf_amendement_with_content(
    app, lecture_senat, article1_senat, amendements_senat
):
    from zam_repondeur.models import DBSession
    from zam_repondeur.services.import_export.pdf import generate_html_for_pdf

    amendement_6666 = amendements_senat[0]
    amendement_6666.auteur = "M. JEAN"
    amendement_6666.groupe = "Les Indépendants"
    amendement_6666.user_content.avis = "Favorable"
    amendement_6666.user_content.objet = "L’objet"
    amendement_6666.user_content.reponse = "La réponse"
    DBSession.add(amendement_6666)

    parser = HTMLParser(
        generate_html_for_pdf(
            DummyRequest(), "print_multiple.html", {"amendements": [amendement_6666]}
        )
    )

    assert _html_page_titles(parser) == ["Réponse", "Amendement nº 6666"]
    response_node = parser.css_first(".reponse")
    assert _cartouche_to_list(response_node) == [
        "Article",
        "Art. 1",
        "Amendement",
        "6666",
        "Auteur",
        "M. JEAN",
        "Groupe",
        "Les Indépendants",
        "Avis",
        "Favorable",
    ]
    assert response_node.css_first("div h5").text() == "Objet"
    assert "L’objet" in response_node.css_first("div p").text()
    assert response_node.css("div h5")[-1].text() == "Réponse"
    assert "La réponse" in response_node.css("div p")[-1].text()


def test_generate_pdf_amendement_with_similaire(
    app, lecture_senat, article1_senat, amendements_senat
):
    from zam_repondeur.models import DBSession
    from zam_repondeur.services.import_export.pdf import generate_html_for_pdf

    amendement_6666, amendement_9999 = amendements_senat
    amendement_6666.auteur = "M. JEAN"
    amendement_6666.groupe = "Les Indépendants"
    amendement_6666.user_content.avis = "Favorable"
    amendement_6666.user_content.objet = "L’objet"
    amendement_6666.user_content.reponse = "La réponse"

    amendement_9999.auteur = "M. CLAUDE"
    amendement_9999.groupe = "Les Mécontents"
    amendement_9999.user_content.avis = "Favorable"
    amendement_9999.user_content.objet = "L’objet"
    amendement_9999.user_content.reponse = "La réponse"

    DBSession.add_all(amendements_senat)

    assert amendement_6666.similaires == [amendement_9999]

    parser = HTMLParser(
        generate_html_for_pdf(
            DummyRequest(), "print_multiple.html", {"amendements": [amendement_6666]}
        )
    )

    assert _html_page_titles(parser) == ["Réponse", "Amendement nº 6666"]
    response_node = parser.css_first(".reponse")
    assert _cartouche_to_list(response_node) == [
        "Article",
        "Art. 1",
        "Amendements",
        "6666 et 9999",
        "Auteurs",
        "M. CLAUDE et M. JEAN",
        "Groupes",
        "Les Indépendants et Les Mécontents",
        "Avis",
        "Favorable",
    ]
    assert response_node.css_first("div h5").text() == "Objet"
    assert "L’objet" in response_node.css_first("div p").text()
    assert response_node.css("div h5")[-1].text() == "Réponse"
    assert "La réponse" in response_node.css("div p")[-1].text()


@pytest.fixture
def another_amendements_an_batch(lecture_an, article1_an):
    from zam_repondeur.models import Amendement, Batch, DBSession

    with transaction.manager:
        batch = Batch.create()
        amendements = [
            Amendement.create(
                lecture=lecture_an,
                article=article1_an,
                num=num,
                position=position,
                batch=batch,
            )
            for position, num in enumerate((555, 888), 3)
        ]
        DBSession.add_all(amendements)

    return amendements


def test_generate_pdf_amendement_with_batches(
    app, lecture_an, amendements_an_batch, another_amendements_an_batch
):
    from zam_repondeur.models import DBSession
    from zam_repondeur.services.import_export.pdf import generate_html_for_pdf

    amendement_666, amendement_999 = amendements_an_batch
    amendement_666.auteur = "M. JEAN"
    amendement_666.groupe = "Les Indépendants"
    amendement_666.user_content.avis = "Favorable"
    amendement_666.user_content.objet = "L’objet"
    amendement_666.user_content.reponse = "La réponse"

    amendement_999.auteur = "M. CLAUDE"
    amendement_999.groupe = "Les Mécontents"
    amendement_999.user_content.avis = "Favorable"
    amendement_999.user_content.objet = "L’objet"
    amendement_999.user_content.reponse = "La réponse"

    amendement_555, amendement_888 = another_amendements_an_batch
    amendement_555.auteur = "M. JACQUES"
    amendement_555.groupe = "Les Indépendants"
    amendement_555.user_content.avis = "Défavorable"
    amendement_555.user_content.objet = "L’autre objet"
    amendement_555.user_content.reponse = "L’autre réponse"

    amendement_888.auteur = "M. ROBERT"
    amendement_888.groupe = "Les Mécontents"
    amendement_888.user_content.avis = "Défavorable"
    amendement_888.user_content.objet = "L’autre objet"
    amendement_888.user_content.reponse = "L’autre réponse"

    DBSession.add_all([amendement_666, amendement_999, amendement_555, amendement_888])

    assert amendement_666.similaires == [amendement_999]
    assert amendement_555.similaires == [amendement_888]

    parser = HTMLParser(
        generate_html_for_pdf(
            DummyRequest(),
            "print_multiple.html",
            {"amendements": [amendement_666, amendement_555]},
        )
    )

    assert _html_page_titles(parser) == [
        "Réponse",
        "Amendement nº 666",
        "Amendement nº 999",
        "Réponse",
        "Amendement nº 555",
        "Amendement nº 888",
    ]
    response_node = parser.css_first(".reponse")
    assert _cartouche_to_list(response_node) == [
        "Article",
        "Art. 1",
        "Amendements",
        "666 et 999",
        "Auteurs",
        "M. CLAUDE et M. JEAN",
        "Groupes",
        "Les Indépendants et Les Mécontents",
        "Avis",
        "Favorable",
    ]
    assert response_node.css_first("div h5").text() == "Objet"
    assert "L’objet" in response_node.css_first("div p").text()
    assert response_node.css("div h5")[-1].text() == "Réponse"
    assert "La réponse" in response_node.css("div p")[-1].text()
