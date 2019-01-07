import transaction

import ujson as json
from pyramid.testing import DummyRequest
from selectolax.parser import HTMLParser


def _csv_row_to_dict(headers, row):
    return dict(zip(headers.split(";"), row.split(";")))


def _html_titles_list(parser, selector="h2"):
    return [node.text().strip() for node in parser.css(selector)]


def _cartouche_to_list(response_node):
    return [
        " ".join(part.strip() for part in node.text().strip().split("\n"))
        for node in response_node.css("table.cartouche tr td")
        if node.text().strip()
    ]


def test_write_json(
    lecture_senat, article1_senat, article1av_senat, article7bis_senat, tmpdir
):
    from zam_repondeur.writer import write_json
    from zam_repondeur.models import Amendement

    filename = str(tmpdir.join("test.json"))

    with transaction.manager:
        article1_senat.user_content.title = "Titre art. 1 Sénat"
        article1_senat.user_content.presentation = "Présentation art. 1 Sénat"
        amendement = Amendement.create(
            lecture=lecture_senat,
            article=article1_senat,
            alinea="",
            num=42,
            rectif=1,
            auteur="M. DUPONT",
            groupe="RDSE",
            matricule="000000",
            dispositif="<p>L'article 1 est supprimé.</p>",
            objet="<p>Cet article va à l'encontre du principe d'égalité.</p>",
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
            objet="baz",
            dispositif="qux",
        )
        Amendement.create(
            lecture=lecture_senat,
            article=article7bis_senat,
            alinea="",
            num=21,
            auteur="M. MARTIN",
            groupe=None,
            matricule="000002",
            objet="quux",
            dispositif="quuz",
        )
        Amendement.create(
            lecture=lecture_senat,
            article=article1_senat,
            alinea="",
            num=43,
            auteur="M. JEAN",
            groupe="Les Indépendants",
            matricule="000003",
            objet="corge",
            dispositif="grault",
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
            objet="corge",
            dispositif="grault",
        )
        nb_rows = write_json(lecture_senat, filename, request={})

    with open(filename, "r", encoding="utf-8-sig") as f_:
        backup = json.loads(f_.read())
        amendements = backup["amendements"]
        articles = backup["articles"]

    assert nb_rows == len(amendements) + len(articles) == 5 + 3

    assert amendements[0] == {
        "alinea": "",
        "auteur": "M. DUPONT",
        "avis": "",
        "chambre": "senat",
        "comments": "",
        "dispositif": "<p>L'article 1 est supprimé.</p>",
        "date_depot": "",
        "id_discussion_commune": "",
        "objet": "<p>Cet article va à l'encontre du principe d'égalité.</p>",
        "groupe": "RDSE",
        "id_identique": "",
        "matricule": "000000",
        "num_texte": 63,
        "article": "Article 1",
        "article_titre": "Titre art. 1 Sénat",
        "parent": "",
        "num": 42,
        "observations": "",
        "organe": "PO78718",
        "position": 1,
        "rectif": 1,
        "reponse": "",
        "affectation": "",
        "resume": "Suppression de l'article",
        "session": "2017-2018",
        "sort": "",
        "gouvernemental": False,
        "article_order": "6|001|01|__________|1",
    }
    assert [amendement["article_order"] for amendement in amendements] == [
        "6|001|01|__________|1",
        "6|007|02|__________|1",
        "6|001|01|__________|1",
        "6|001|01|__________|0",
        "6|001|01|__________|1",
    ]
    assert articles == [
        {"presentation": "", "sort_key_as_str": "6|001|01|__________|0", "title": ""},
        {
            "presentation": "Présentation art. 1 Sénat",
            "sort_key_as_str": "6|001|01|__________|1",
            "title": "Titre art. 1 Sénat",
        },
        {"presentation": "", "sort_key_as_str": "6|007|02|__________|1", "title": ""},
    ]


def test_write_json_full(lecture_senat, article1_senat, tmpdir):
    from zam_repondeur.writer import write_json
    from zam_repondeur.models import Amendement

    filename = str(tmpdir.join("test.json"))

    with transaction.manager:
        Amendement.create(
            lecture=lecture_senat,
            article=article1_senat,
            alinea="",
            num=42,
            rectif=1,
            auteur="M. DUPONT",
            groupe="RDSE",
            matricule="000000",
            dispositif="<p>L'article 1 est supprimé.</p>",
            objet="<p>Cet article va à l'encontre du principe d'égalité.</p>",
            resume="Suppression de l'article",
            position=1,
            avis="Défavorable",
            observations="Un objet",
            reponse="<p>La réponse</p>",
            affectation="4C",
            comments="<strong>Lisez-moi</strong>",
        )
        nb_rows = write_json(lecture_senat, filename, request={})

    with open(filename, "r", encoding="utf-8-sig") as f_:
        backup = json.loads(f_.read())
        amendements = backup["amendements"]
        articles = backup["articles"]

    assert nb_rows == len(amendements) + len(articles) == 1 + 1

    assert amendements[0] == {
        "alinea": "",
        "auteur": "M. DUPONT",
        "avis": "Défavorable",
        "chambre": "senat",
        "comments": "<strong>Lisez-moi</strong>",
        "dispositif": "<p>L'article 1 est supprimé.</p>",
        "date_depot": "",
        "id_discussion_commune": "",
        "objet": "<p>Cet article va à l'encontre du principe d'égalité.</p>",
        "groupe": "RDSE",
        "id_identique": "",
        "matricule": "000000",
        "num_texte": 63,
        "article": "Article 1",
        "article_titre": "",
        "parent": "",
        "num": 42,
        "observations": "Un objet",
        "organe": "PO78718",
        "position": 1,
        "rectif": 1,
        "reponse": "<p>La réponse</p>",
        "affectation": "4C",
        "resume": "Suppression de l'article",
        "session": "2017-2018",
        "sort": "",
        "gouvernemental": False,
        "article_order": "6|001|01|__________|1",
    }


def test_write_json_sous_amendement(
    lecture_senat, article1_senat, article1av_senat, article7bis_senat, tmpdir
):
    from zam_repondeur.writer import write_json
    from zam_repondeur.models import Amendement

    filename = str(tmpdir.join("test.json"))

    with transaction.manager:
        amendement = Amendement.create(
            lecture=lecture_senat,
            article=article1_senat,
            alinea="",
            num=42,
            rectif=1,
            auteur="M. DUPONT",
            groupe="RDSE",
            matricule="000000",
            dispositif="<p>L'article 1 est supprimé.</p>",
            objet="<p>Cet article va à l'encontre du principe d'égalité.</p>",
            resume="Suppression de l'article",
        )
        Amendement.create(
            lecture=lecture_senat,
            article=article1av_senat,
            alinea="",
            num=57,
            auteur="M. DURAND",
            groupe="Les Républicains",
            matricule="000001",
            objet="baz",
            dispositif="qux",
        )
        Amendement.create(
            lecture=lecture_senat,
            article=article7bis_senat,
            alinea="",
            num=21,
            auteur="M. MARTIN",
            groupe=None,
            matricule="000002",
            objet="quux",
            dispositif="quuz",
        )
        Amendement.create(
            lecture=lecture_senat,
            article=article1_senat,
            alinea="",
            num=43,
            auteur="M. JEAN",
            groupe="Les Indépendants",
            matricule="000003",
            objet="corge",
            dispositif="grault",
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
            objet="corge",
            dispositif="grault",
        )
        nb_rows = write_json(lecture_senat, filename, request={})

    with open(filename, "r", encoding="utf-8-sig") as f_:
        backup = json.loads(f_.read())
        amendements = backup["amendements"]
        articles = backup["articles"]

    assert nb_rows == len(amendements) + len(articles) == 5 + 3

    assert amendements[-1] == {
        "alinea": "",
        "auteur": "M. JEAN",
        "avis": "",
        "article_order": "6|001|01|__________|1",
        "chambre": "senat",
        "comments": "",
        "dispositif": "grault",
        "date_depot": "",
        "id_discussion_commune": "",
        "objet": "corge",
        "groupe": "Les Indépendants",
        "id_identique": "",
        "matricule": "000003",
        "num_texte": 63,
        "article": "Article 1",
        "article_titre": "",
        "parent": "42 rect.",
        "num": 596,
        "observations": "",
        "organe": "PO78718",
        "position": "",
        "rectif": 1,
        "reponse": "",
        "affectation": "",
        "resume": "",
        "session": "2017-2018",
        "sort": "",
        "gouvernemental": False,
    }


def test_generate_pdf_without_responses(
    app, lecture_senat, article1_senat, article1av_senat, article7bis_senat
):
    from zam_repondeur.writer import generate_html_for_pdf
    from zam_repondeur.models import Amendement

    amendement = Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=42,
        rectif=1,
        auteur="M. DUPONT",
        groupe="RDSE",
        matricule="000000",
        dispositif="<p>L'article 1 est supprimé.</p>",
        objet="<p>Cet article va à l'encontre du principe d'égalité.</p>",
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
        objet="baz",
        dispositif="qux",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article7bis_senat,
        alinea="",
        num=21,
        auteur="M. MARTIN",
        groupe=None,
        matricule="000002",
        objet="quux",
        dispositif="quuz",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=43,
        auteur="M. JEAN",
        groupe="Les Indépendants",
        matricule="000003",
        objet="corge",
        dispositif="grault",
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
        objet="corge",
        dispositif="grault",
    )
    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )
    assert parser.css_first("h1").text() == "Titre dossier legislatif sénat"
    assert _html_titles_list(parser) == [
        "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063",
        "Article 1",
        "Article 7 bis",
    ]


def test_generate_pdf_with_amendement_responses(
    app, lecture_senat, article1_senat, article1av_senat, article7bis_senat
):
    from zam_repondeur.writer import generate_html_for_pdf
    from zam_repondeur.models import Amendement

    amendement = Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=42,
        rectif=1,
        auteur="M. DUPONT",
        groupe="RDSE",
        matricule="000000",
        dispositif="<p>L'article 1 est supprimé.</p>",
        objet="<p>Cet article va à l'encontre du principe d'égalité.</p>",
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
        objet="baz",
        dispositif="qux",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article7bis_senat,
        alinea="",
        num=21,
        auteur="M. MARTIN",
        groupe=None,
        matricule="000002",
        objet="quux",
        dispositif="quuz",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=43,
        auteur="M. JEAN",
        groupe="Les Indépendants",
        matricule="000003",
        objet="corge",
        dispositif="grault",
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
        objet="corge",
        dispositif="grault",
    )
    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )
    assert _html_titles_list(parser) == [
        "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063",
        "Article 1",
        "Réponse",
        "Amendement nº 42 rect.",
        "Article 7 bis",
    ]


def test_generate_pdf_with_amendement_content(
    app, lecture_senat, article1_senat, amendements_senat
):
    from zam_repondeur.writer import generate_html_for_pdf
    from zam_repondeur.models import DBSession, Lecture

    amendement_6666 = amendements_senat[0]
    amendement_6666.auteur = "M. JEAN"
    amendement_6666.groupe = "Les Indépendants"
    amendement_6666.avis = "Favorable"
    amendement_6666.observations = "Les observations"
    amendement_6666.reponse = "La réponse"
    DBSession.add(amendement_6666)
    lecture_senat = (
        DBSession.query(Lecture)
        .filter(Lecture.num_texte == lecture_senat.num_texte)
        .first()
    )
    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )
    assert _html_titles_list(parser) == [
        "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063",
        "Article 1",
        "Réponse",
        "Amendement nº 6666",
    ]
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
    assert response_node.css_first("div h3").text() == "Objet"
    assert "Les observations" in response_node.css_first("div p").text()
    assert response_node.css("div h3")[-1].text() == "Réponse"
    assert "La réponse" in response_node.css("div p")[-1].text()


def test_generate_pdf_with_amendement_content_factor_authors_groups(
    app, lecture_senat, article1_senat, amendements_senat
):
    from zam_repondeur.writer import generate_html_for_pdf
    from zam_repondeur.models import DBSession, Lecture

    amendement_6666 = amendements_senat[0]
    amendement_6666.auteur = "M. JEAN"
    amendement_6666.groupe = "Les Indépendants"
    amendement_6666.avis = "Favorable"
    amendement_6666.observations = "Les observations"
    amendement_6666.reponse = "La réponse"
    DBSession.add(amendement_6666)
    amendement_9999 = amendements_senat[1]
    amendement_9999.auteur = "M. JEAN"
    amendement_9999.groupe = "Les Indépendants"
    amendement_9999.avis = "Favorable"
    amendement_9999.observations = "Les observations"
    amendement_9999.reponse = "La réponse"
    DBSession.add(amendement_9999)
    lecture_senat = (
        DBSession.query(Lecture)
        .filter(Lecture.num_texte == lecture_senat.num_texte)
        .first()
    )
    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )
    assert _html_titles_list(parser) == [
        "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063",
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
    assert response_node.css_first("div h3").text() == "Objet"
    assert "Les observations" in response_node.css_first("div p").text()
    assert response_node.css("div h3")[-1].text() == "Réponse"
    assert "La réponse" in response_node.css("div p")[-1].text()


def test_generate_pdf_with_amendement_content_factor_only_groups(
    app, lecture_senat, article1_senat, amendements_senat
):
    from zam_repondeur.writer import generate_html_for_pdf
    from zam_repondeur.models import DBSession, Lecture

    amendement_6666 = amendements_senat[0]
    amendement_6666.auteur = "M. JEAN"
    amendement_6666.groupe = "Les Indépendants"
    amendement_6666.avis = "Favorable"
    amendement_6666.observations = "Les observations"
    amendement_6666.reponse = "La réponse"
    DBSession.add(amendement_6666)
    amendement_9999 = amendements_senat[1]
    amendement_9999.auteur = "M. CLAUDE"
    amendement_9999.groupe = "Les Indépendants"
    amendement_9999.avis = "Favorable"
    amendement_9999.observations = "Les observations"
    amendement_9999.reponse = "La réponse"
    DBSession.add(amendement_9999)
    lecture_senat = (
        DBSession.query(Lecture)
        .filter(Lecture.num_texte == lecture_senat.num_texte)
        .first()
    )
    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )
    assert _html_titles_list(parser) == [
        "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063",
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
    assert response_node.css_first("div h3").text() == "Objet"
    assert "Les observations" in response_node.css_first("div p").text()
    assert response_node.css("div h3")[-1].text() == "Réponse"
    assert "La réponse" in response_node.css("div p")[-1].text()


def test_generate_pdf_with_amendement_content_factor_many_authors_groups(
    app, lecture_senat, article1_senat, amendements_senat
):
    from zam_repondeur.writer import generate_html_for_pdf
    from zam_repondeur.models import Amendement, DBSession, Lecture

    amendement_6666 = amendements_senat[0]
    amendement_6666.auteur = "M. JEAN"
    amendement_6666.groupe = "Les Indépendants"
    amendement_6666.avis = "Défavorable"
    amendement_6666.observations = "Les observations"
    amendement_6666.reponse = "La réponse"
    DBSession.add(amendement_6666)
    amendement_9999 = amendements_senat[1]
    amendement_9999.auteur = "M. JEAN"
    amendement_9999.groupe = "Les Indépendants"
    amendement_9999.avis = "Défavorable"
    amendement_9999.observations = "Les observations"
    amendement_9999.reponse = "La réponse"
    DBSession.add(amendement_9999)
    Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        num=42,
        position=3,
        auteur="M. DUPONT",
        groupe="RDSE",
        avis="Défavorable",
        observations="Les observations",
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
        observations="Les observations",
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
        observations="Les observations",
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
        observations="Les observations",
        reponse="La réponse",
    )
    lecture_senat = (
        DBSession.query(Lecture)
        .filter(Lecture.num_texte == lecture_senat.num_texte)
        .first()
    )
    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )
    assert _html_titles_list(parser) == [
        "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063",
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
    assert response_node.css_first("div h3").text() == "Objet"
    assert "Les observations" in response_node.css_first("div p").text()
    assert response_node.css("div h3")[-1].text() == "Réponse"
    assert "La réponse" in response_node.css("div p")[-1].text()


def test_generate_pdf_with_amendement_content_gouvernemental(
    app, lecture_senat, article1_senat, amendements_senat
):
    from zam_repondeur.writer import generate_html_for_pdf
    from zam_repondeur.models import DBSession, Lecture

    amendement_6666 = amendements_senat[0]
    amendement_6666.auteur = "LE GOUVERNEMENT"
    amendement_6666.reponse = "La présentation"
    DBSession.add(amendement_6666)
    lecture_senat = (
        DBSession.query(Lecture)
        .filter(Lecture.num_texte == lecture_senat.num_texte)
        .first()
    )
    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )
    assert _html_titles_list(parser) == [
        "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063",
        "Article 1",
        "Réponse",
        "Amendement nº 6666",
    ]
    response_node = parser.css_first(".reponse")
    assert _cartouche_to_list(response_node) == [
        "Article",
        "Art. 1",
        "Amendement",
        "6666",
        "Auteur",
        "Gouvernement",
    ]
    assert response_node.css_first("div h3").text() == "Réponse"
    assert "La présentation" in response_node.css_first("div p").text()


def test_generate_pdf_with_amendement_and_sous_amendement_responses(
    app, lecture_senat, article1_senat, article1av_senat, article7bis_senat
):
    from zam_repondeur.writer import generate_html_for_pdf
    from zam_repondeur.models import Amendement

    amendement = Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=42,
        rectif=1,
        auteur="M. DUPONT",
        groupe="RDSE",
        matricule="000000",
        dispositif="<p>L'article 1 est supprimé.</p>",
        objet="<p>Cet article va à l'encontre du principe d'égalité.</p>",
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
        objet="baz",
        dispositif="qux",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article7bis_senat,
        alinea="",
        num=21,
        auteur="M. MARTIN",
        groupe=None,
        matricule="000002",
        objet="quux",
        dispositif="quuz",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=43,
        auteur="M. JEAN",
        groupe="Les Indépendants",
        matricule="000003",
        objet="corge",
        dispositif="grault",
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
        objet="corge",
        dispositif="grault",
        avis="Défavorable",
    )
    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )
    assert _html_titles_list(parser) == [
        "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063",
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
    from zam_repondeur.writer import generate_html_for_pdf
    from zam_repondeur.models import Amendement

    amendement = Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=42,
        rectif=1,
        auteur="M. DUPONT",
        groupe="RDSE",
        matricule="000000",
        dispositif="<p>L'article 1 est supprimé.</p>",
        objet="<p>Cet article va à l'encontre du principe d'égalité.</p>",
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
        objet="baz",
        dispositif="qux",
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
        objet="quux",
        dispositif="quuz",
    )
    Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=43,
        auteur="M. JEAN",
        groupe="Les Indépendants",
        matricule="000003",
        objet="corge",
        dispositif="grault",
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
        objet="corge",
        dispositif="grault",
    )
    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )
    assert _html_titles_list(parser) == [
        "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063",
        "Réponse",
        "Amendement nº 57",
        "Article 1",
        "Réponse",
        "Amendement nº 42 rect.",
        "Article 7 bis",
    ]


def test_generate_pdf_unitary_without_responses(app, lecture_senat, article1_senat):
    from zam_repondeur.writer import generate_html_for_pdf
    from zam_repondeur.models import Amendement

    amendement = Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=42,
        rectif=1,
        auteur="M. DUPONT",
        groupe="RDSE",
        matricule="000000",
        dispositif="<p>L'article 1 est supprimé.</p>",
        objet="<p>Cet article va à l'encontre du principe d'égalité.</p>",
        resume="Suppression de l'article",
        position=1,
    )
    parser = HTMLParser(
        generate_html_for_pdf(
            DummyRequest(), "print1.html", {"amendement": amendement, "similaires": []}
        )
    )
    assert _html_titles_list(parser) == ["Amendement nº 42 rect."]


def test_generate_pdf_unitary_with_amendement_responses(
    app, lecture_senat, article1_senat
):
    from zam_repondeur.writer import generate_html_for_pdf
    from zam_repondeur.models import Amendement

    amendement = Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=42,
        rectif=1,
        auteur="M. DUPONT",
        groupe="RDSE",
        matricule="000000",
        dispositif="<p>L'article 1 est supprimé.</p>",
        objet="<p>Cet article va à l'encontre du principe d'égalité.</p>",
        resume="Suppression de l'article",
        position=1,
        avis="Favorable",
    )
    parser = HTMLParser(
        generate_html_for_pdf(
            DummyRequest(), "print1.html", {"amendement": amendement, "similaires": []}
        )
    )
    assert _html_titles_list(parser) == ["Réponse", "Amendement nº 42 rect."]


def test_generate_pdf_unitary_with_amendement_content(
    app, lecture_senat, article1_senat, amendements_senat
):
    from zam_repondeur.writer import generate_html_for_pdf
    from zam_repondeur.models import DBSession

    amendement_6666 = amendements_senat[0]
    amendement_6666.auteur = "M. JEAN"
    amendement_6666.groupe = "Les Indépendants"
    amendement_6666.avis = "Favorable"
    amendement_6666.observations = "Les observations"
    amendement_6666.reponse = "La réponse"
    DBSession.add(amendement_6666)
    parser = HTMLParser(
        generate_html_for_pdf(
            DummyRequest(),
            "print1.html",
            {"amendement": amendement_6666, "similaires": []},
        )
    )
    assert _html_titles_list(parser) == ["Réponse", "Amendement nº 6666"]
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
    assert response_node.css_first("div h3").text() == "Objet"
    assert "Les observations" in response_node.css_first("div p").text()
    assert response_node.css("div h3")[-1].text() == "Réponse"
    assert "La réponse" in response_node.css("div p")[-1].text()


def test_generate_pdf_unitary_with_amendement_similaire(
    app, lecture_senat, article1_senat, amendements_senat
):
    from zam_repondeur.writer import generate_html_for_pdf
    from zam_repondeur.models import DBSession

    amendement_6666, amendement_9999 = amendements_senat
    amendement_6666.auteur = "M. JEAN"
    amendement_6666.groupe = "Les Indépendants"
    amendement_6666.avis = "Favorable"
    amendement_6666.observations = "Les observations"
    amendement_6666.reponse = "La réponse"
    amendement_9999.auteur = "M. CLAUDE"
    amendement_9999.groupe = "Les Mécontents"
    amendement_9999.avis = "Favorable"
    amendement_9999.observations = "Les observations"
    amendement_9999.reponse = "La réponse"
    DBSession.add_all(amendements_senat)
    parser = HTMLParser(
        generate_html_for_pdf(
            DummyRequest(),
            "print1.html",
            {"amendement": amendement_6666, "similaires": [amendement_9999]},
        )
    )
    assert _html_titles_list(parser) == ["Réponse", "Amendement nº 6666"]
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
    assert response_node.css_first("div h3").text() == "Objet"
    assert "Les observations" in response_node.css_first("div p").text()
    assert response_node.css("div h3")[-1].text() == "Réponse"
    assert "La réponse" in response_node.css("div p")[-1].text()
