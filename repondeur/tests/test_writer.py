import transaction
from datetime import datetime

from pyramid.testing import DummyRequest
from selectolax.parser import HTMLParser


def _csv_row_to_dict(headers, row):
    return dict(zip(headers.split(";"), row.split(";")))


def _html_titles_list(parser, selector="h2"):
    return [node.text().strip() for node in parser.css(selector)]


def test_write_csv(
    lecture_senat, article1_senat, article1av_senat, article7bis_senat, tmpdir
):
    from zam_repondeur.writer import write_csv
    from zam_repondeur.models import DBSession, Amendement

    filename = str(tmpdir.join("test.csv"))

    with transaction.manager:
        amendement = Amendement(
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
        amendements = [
            amendement,
            Amendement(
                lecture=lecture_senat,
                article=article1av_senat,
                alinea="",
                num=57,
                auteur="M. DURAND",
                groupe="Les Républicains",
                matricule="000001",
                objet="baz",
                dispositif="qux",
            ),
            Amendement(
                lecture=lecture_senat,
                article=article7bis_senat,
                alinea="",
                num=21,
                auteur="M. MARTIN",
                groupe=None,
                matricule="000002",
                objet="quux",
                dispositif="quuz",
            ),
            Amendement(
                lecture=lecture_senat,
                article=article1_senat,
                alinea="",
                num=43,
                auteur="M. JEAN",
                groupe="Les Indépendants",
                matricule="000003",
                objet="corge",
                dispositif="grault",
            ),
            Amendement(
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
            ),
        ]
        DBSession.add_all(amendements)
        nb_rows = write_csv(lecture_senat, filename, request={})

    with open(filename, "r", encoding="utf-8-sig", newline="\n") as f_:
        lines = [line.rstrip("\n") for line in f_]

    assert not any(line.endswith("\r") for line in lines)

    headers, *rows = lines

    assert len(rows) == nb_rows == 5

    assert _csv_row_to_dict(headers, rows[0]) == {
        "Alinéa": "",
        "Auteur(s)": "M. DUPONT",
        "Avis du Gouvernement": "",
        "Chambre": "senat",
        "Commentaires": "",
        "Corps amdt": "L'article 1 est supprimé.",
        "Date de dépôt": "",
        "Discussion commune ?": "",
        "Exposé amdt": "Cet article va à l'encontre du principe d'égalité.",
        "Groupe": "RDSE",
        "Identique ?": "",
        "Matricule": "000000",
        "Num_texte": "63",
        "Num article": "Article 1",
        "Titre article": "",
        "Parent": "",
        "Num amdt": "42",
        "Objet amdt": "",
        "Organe": "PO78718",
        "Position": "1",
        "Rectif": "1",
        "Réponse": "",
        "Resume": "Suppression de l'article",
        "Session": "2017-2018",
        "Signalé": "Non",
        "Sort": "",
        "Gouvernemental": "False",
    }


def test_write_csv_sous_amendement(
    lecture_senat, article1_senat, article1av_senat, article7bis_senat, tmpdir
):
    from zam_repondeur.writer import write_csv
    from zam_repondeur.models import DBSession, Amendement

    filename = str(tmpdir.join("test.csv"))

    with transaction.manager:
        amendement = Amendement(
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
        amendements = [
            amendement,
            Amendement(
                lecture=lecture_senat,
                article=article1av_senat,
                alinea="",
                num=57,
                auteur="M. DURAND",
                groupe="Les Républicains",
                matricule="000001",
                objet="baz",
                dispositif="qux",
            ),
            Amendement(
                lecture=lecture_senat,
                article=article7bis_senat,
                alinea="",
                num=21,
                auteur="M. MARTIN",
                groupe=None,
                matricule="000002",
                objet="quux",
                dispositif="quuz",
            ),
            Amendement(
                lecture=lecture_senat,
                article=article1_senat,
                alinea="",
                num=43,
                auteur="M. JEAN",
                groupe="Les Indépendants",
                matricule="000003",
                objet="corge",
                dispositif="grault",
            ),
            Amendement(
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
                bookmarked_at=datetime.now(),
            ),
        ]
        DBSession.add_all(amendements)
        nb_rows = write_csv(lecture_senat, filename, request={})

    with open(filename, "r", encoding="utf-8-sig", newline="\n") as f_:
        lines = [line.rstrip("\n") for line in f_]

    assert not any(line.endswith("\r") for line in lines)

    headers, *rows = lines

    assert len(rows) == nb_rows == 5

    assert _csv_row_to_dict(headers, rows[-1]) == {
        "Chambre": "senat",
        "Session": "2017-2018",
        "Signalé": "Oui",
        "Num_texte": "63",
        "Organe": "PO78718",
        "Num article": "Article 1",
        "Titre article": "",
        "Alinéa": "",
        "Num amdt": "596",
        "Rectif": "1",
        "Auteur(s)": "M. JEAN",
        "Matricule": "000003",
        "Groupe": "Les Indépendants",
        "Date de dépôt": "",
        "Sort": "",
        "Position": "",
        "Discussion commune ?": "",
        "Identique ?": "",
        "Parent": "42 rect.",
        "Corps amdt": "grault",
        "Exposé amdt": "corge",
        "Avis du Gouvernement": "",
        "Objet amdt": "",
        "Réponse": "",
        "Gouvernemental": "False",
        "Commentaires": "",
        "Resume": "",
    }


def test_generate_pdf_without_responses(
    app, lecture_senat, article1_senat, article1av_senat, article7bis_senat
):
    from zam_repondeur.writer import generate_html_for_pdf
    from zam_repondeur.models import DBSession, Amendement

    amendement = Amendement(
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
    amendements = [
        amendement,
        Amendement(
            lecture=lecture_senat,
            article=article1av_senat,
            alinea="",
            num=57,
            auteur="M. DURAND",
            groupe="Les Républicains",
            matricule="000001",
            objet="baz",
            dispositif="qux",
        ),
        Amendement(
            lecture=lecture_senat,
            article=article7bis_senat,
            alinea="",
            num=21,
            auteur="M. MARTIN",
            groupe=None,
            matricule="000002",
            objet="quux",
            dispositif="quuz",
        ),
        Amendement(
            lecture=lecture_senat,
            article=article1_senat,
            alinea="",
            num=43,
            auteur="M. JEAN",
            groupe="Les Indépendants",
            matricule="000003",
            objet="corge",
            dispositif="grault",
        ),
        Amendement(
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
        ),
    ]
    DBSession.add_all(amendements)
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
    from zam_repondeur.models import DBSession, Amendement

    amendement = Amendement(
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
    amendements = [
        amendement,
        Amendement(
            lecture=lecture_senat,
            article=article1av_senat,
            alinea="",
            num=57,
            auteur="M. DURAND",
            groupe="Les Républicains",
            matricule="000001",
            objet="baz",
            dispositif="qux",
        ),
        Amendement(
            lecture=lecture_senat,
            article=article7bis_senat,
            alinea="",
            num=21,
            auteur="M. MARTIN",
            groupe=None,
            matricule="000002",
            objet="quux",
            dispositif="quuz",
        ),
        Amendement(
            lecture=lecture_senat,
            article=article1_senat,
            alinea="",
            num=43,
            auteur="M. JEAN",
            groupe="Les Indépendants",
            matricule="000003",
            objet="corge",
            dispositif="grault",
        ),
        Amendement(
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
        ),
    ]
    DBSession.add_all(amendements)
    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )
    assert _html_titles_list(parser) == [
        "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063",
        "Article 1",
        "Réponse",
        "Amendement",
        "Article 7 bis",
    ]


def test_generate_pdf_with_amendement_and_sous_amendement_responses(
    app, lecture_senat, article1_senat, article1av_senat, article7bis_senat
):
    from zam_repondeur.writer import generate_html_for_pdf
    from zam_repondeur.models import DBSession, Amendement

    amendement = Amendement(
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
    amendements = [
        amendement,
        Amendement(
            lecture=lecture_senat,
            article=article1av_senat,
            alinea="",
            num=57,
            auteur="M. DURAND",
            groupe="Les Républicains",
            matricule="000001",
            objet="baz",
            dispositif="qux",
        ),
        Amendement(
            lecture=lecture_senat,
            article=article7bis_senat,
            alinea="",
            num=21,
            auteur="M. MARTIN",
            groupe=None,
            matricule="000002",
            objet="quux",
            dispositif="quuz",
        ),
        Amendement(
            lecture=lecture_senat,
            article=article1_senat,
            alinea="",
            num=43,
            auteur="M. JEAN",
            groupe="Les Indépendants",
            matricule="000003",
            objet="corge",
            dispositif="grault",
        ),
        Amendement(
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
        ),
    ]
    DBSession.add_all(amendements)
    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )
    assert _html_titles_list(parser) == [
        "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063",
        "Article 1",
        "Réponse",
        "Amendement",
        "Réponse",
        "Sous-amendement",
        "Article 7 bis",
    ]


def test_generate_pdf_with_additional_article_amendements_having_responses(
    app, lecture_senat, article1_senat, article1av_senat, article7bis_senat
):
    from zam_repondeur.writer import generate_html_for_pdf
    from zam_repondeur.models import DBSession, Amendement

    amendement = Amendement(
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
    amendements = [
        amendement,
        Amendement(
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
        ),
        Amendement(
            lecture=lecture_senat,
            article=article7bis_senat,
            alinea="",
            num=21,
            auteur="M. MARTIN",
            groupe=None,
            matricule="000002",
            objet="quux",
            dispositif="quuz",
        ),
        Amendement(
            lecture=lecture_senat,
            article=article1_senat,
            alinea="",
            num=43,
            auteur="M. JEAN",
            groupe="Les Indépendants",
            matricule="000003",
            objet="corge",
            dispositif="grault",
        ),
        Amendement(
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
        ),
    ]
    DBSession.add_all(amendements)
    parser = HTMLParser(
        generate_html_for_pdf(DummyRequest(), "print.html", {"lecture": lecture_senat})
    )
    assert _html_titles_list(parser) == [
        "Sénat, session 2017-2018, Séance publique, Numéro lecture, texte nº\xa063",
        "Réponse",
        "Amendement",
        "Article 1",
        "Réponse",
        "Amendement",
        "Article 7 bis",
    ]
