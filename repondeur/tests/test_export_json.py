import transaction

import ujson as json


def test_write_json(
    lecture_senat, article1_senat, article1av_senat, article7bis_senat, tmpdir
):
    from zam_repondeur.export.json import write_json
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
        counter = write_json(lecture_senat, filename, request={})

    with open(filename, "r", encoding="utf-8-sig") as f_:
        backup = json.loads(f_.read())
        amendements = backup["amendements"]
        articles = backup["articles"]

    assert counter["amendements"] == len(amendements) == 5
    assert counter["articles"] == len(articles) == 3

    assert amendements[0] == {
        "alinea": "",
        "auteur": "M. DUPONT",
        "avis": "",
        "chambre": "senat",
        "comments": "",
        "corps": "<p>L'article 1 est supprimé.</p>",
        "date_depot": "",
        "id_discussion_commune": "",
        "expose": "<p>Cet article va à l'encontre du principe d'égalité.</p>",
        "groupe": "RDSE",
        "id_identique": "",
        "matricule": "000000",
        "num_texte": 63,
        "article": "Article 1",
        "article_titre": "Titre art. 1 Sénat",
        "parent": "",
        "num": 42,
        "objet": "",
        "organe": "PO78718",
        "position": 1,
        "rectif": 1,
        "reponse": "",
        "resume": "Suppression de l'article",
        "legislature": "",
        "session": "2017-2018",
        "sort": "",
        "gouvernemental": False,
        "article_order": "6|001|01|__________|1",
        "affectation_email": "",
        "affectation_name": "",
    }
    assert [amdt["article_order"] for amdt in amendements] == [
        "6|001|01|__________|1",
        "6|001|01|__________|0",
        "6|001|01|__________|1",
        "6|001|01|__________|1",
        "6|007|02|__________|1",
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
    from zam_repondeur.export.json import write_json
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
            corps="<p>L'article 1 est supprimé.</p>",
            expose="<p>Cet article va à l'encontre du principe d'égalité.</p>",
            resume="Suppression de l'article",
            position=1,
            avis="Défavorable",
            objet="Un objet",
            reponse="<p>La réponse</p>",
            comments="<strong>Lisez-moi</strong>",
        )
        counter = write_json(lecture_senat, filename, request={})

    with open(filename, "r", encoding="utf-8-sig") as f_:
        backup = json.loads(f_.read())
        amendements = backup["amendements"]
        articles = backup["articles"]

    assert counter["amendements"] == len(amendements) == 1
    assert counter["articles"] == len(articles) == 1

    assert amendements[0] == {
        "alinea": "",
        "auteur": "M. DUPONT",
        "avis": "Défavorable",
        "chambre": "senat",
        "comments": "<strong>Lisez-moi</strong>",
        "corps": "<p>L'article 1 est supprimé.</p>",
        "date_depot": "",
        "id_discussion_commune": "",
        "expose": "<p>Cet article va à l'encontre du principe d'égalité.</p>",
        "groupe": "RDSE",
        "id_identique": "",
        "matricule": "000000",
        "num_texte": 63,
        "article": "Article 1",
        "article_titre": "",
        "parent": "",
        "num": 42,
        "objet": "Un objet",
        "organe": "PO78718",
        "position": 1,
        "rectif": 1,
        "reponse": "<p>La réponse</p>",
        "resume": "Suppression de l'article",
        "legislature": "",
        "session": "2017-2018",
        "sort": "",
        "gouvernemental": False,
        "article_order": "6|001|01|__________|1",
        "affectation_email": "",
        "affectation_name": "",
    }


def test_write_with_affectation(
    lecture_senat, article1_senat, tmpdir, user_david_table_senat
):
    from zam_repondeur.export.json import write_json
    from zam_repondeur.models import Amendement, DBSession

    filename = str(tmpdir.join("test.json"))

    with transaction.manager:
        DBSession.add(user_david_table_senat)
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
        )
        user_david_table_senat.amendements.append(amendement)

        counter = write_json(lecture_senat, filename, request={})

    with open(filename, "r", encoding="utf-8-sig") as f_:
        backup = json.loads(f_.read())
        amendements = backup["amendements"]
        articles = backup["articles"]

    assert counter["amendements"] == len(amendements) == 1
    assert counter["articles"] == len(articles) == 1
    assert amendements[0]["affectation_email"] == "david@exemple.gouv.fr"
    assert amendements[0]["affectation_name"] == "David"


def test_write_json_sous_amendement(
    lecture_senat, article1_senat, article1av_senat, article7bis_senat, tmpdir
):
    from zam_repondeur.export.json import write_json
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
            corps="<p>L'article 1 est supprimé.</p>",
            expose="<p>Cet article va à l'encontre du principe d'égalité.</p>",
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
        counter = write_json(lecture_senat, filename, request={})

    with open(filename, "r", encoding="utf-8-sig") as f_:
        backup = json.loads(f_.read())
        amendements = backup["amendements"]
        articles = backup["articles"]

    assert counter["amendements"] == len(amendements) == 5
    assert counter["articles"] == len(articles) == 3

    assert amendements[-2] == {
        "alinea": "",
        "auteur": "M. JEAN",
        "avis": "",
        "article_order": "6|001|01|__________|1",
        "chambre": "senat",
        "comments": "",
        "expose": "grault",
        "date_depot": "",
        "id_discussion_commune": "",
        "corps": "corge",
        "groupe": "Les Indépendants",
        "id_identique": "",
        "matricule": "000003",
        "num_texte": 63,
        "article": "Article 1",
        "article_titre": "",
        "parent": "42 rect.",
        "num": 596,
        "objet": "",
        "organe": "PO78718",
        "position": "",
        "rectif": 1,
        "reponse": "",
        "resume": "",
        "legislature": "",
        "session": "2017-2018",
        "sort": "",
        "gouvernemental": False,
        "affectation_email": "",
        "affectation_name": "",
    }


class TestAmendementsHaveSessionOrLegislature:
    def test_an_amendements_have_legislature(self, lecture_an, amendements_an, tmpdir):
        from zam_repondeur.export.json import write_json
        from zam_repondeur.models import DBSession

        DBSession.add(lecture_an)

        filename = str(tmpdir.join("test.json"))

        write_json(lecture_an, filename, request={})

        with open(filename, "r", encoding="utf-8-sig") as f_:
            export = json.loads(f_.read())

        for amendement in export["amendements"]:
            assert amendement["legislature"] == 15
            assert amendement["session"] == ""

    def test_senat_amendements_have_session(
        self, lecture_senat, amendements_senat, tmpdir
    ):
        from zam_repondeur.export.json import write_json
        from zam_repondeur.models import DBSession

        DBSession.add(lecture_senat)

        filename = str(tmpdir.join("test.json"))

        write_json(lecture_senat, filename, request={})

        with open(filename, "r", encoding="utf-8-sig") as f_:
            export = json.loads(f_.read())

        for amendement in export["amendements"]:
            assert amendement["legislature"] == ""
            assert amendement["session"] == "2017-2018"
