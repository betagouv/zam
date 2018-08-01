import transaction


def _csv_row_to_dict(headers, row):
    return dict(zip(headers.split(";"), row.split(";")))


def test_write_csv(lecture_senat, article1, article1av, article7bis, tmpdir):
    from zam_repondeur.writer import write_csv
    from zam_repondeur.models import DBSession, Amendement

    filename = str(tmpdir.join("test.csv"))

    with transaction.manager:
        amendement = Amendement(
            lecture=lecture_senat,
            article=article1,
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
                article=article1av,
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
                article=article7bis,
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
                article=article1,
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
                article=article1,
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
        nb_rows = write_csv("Titre", amendements, filename, request={})

    with open(filename, "r", encoding="utf-8") as f_:
        lines = f_.read().splitlines()
    headers, *rows = lines

    assert len(rows) == nb_rows == 5

    assert _csv_row_to_dict(headers, rows[0]) == {
        "Pk": "000042",
        "Alinéa": "",
        "Auteur(s)": "M. DUPONT",
        "Avis du Gouvernement": "",
        "Chambre": "senat",
        "Commentaires": "",
        "Corps amdt": "Cet article va à l'encontre du principe d'égalité.",
        "Date de dépôt": "",
        "Discussion commune ?": "",
        "Dispositif": "L'article 1 est supprimé.",
        "Exposé amdt": "Suppression de l'article",
        "Groupe": "RDSE",
        "Identique ?": "",
        "Matricule": "000000",
        "Num_texte": "63",
        "Parent": "",
        "Nº amdt": "42",
        "Objet amdt": "",
        "Organe": "PO78718",
        "Position": "",
        "Rectif": "1",
        "Réponse": "",
        "Session": "2017-2018",
        "Sort": "",
        "Subdiv_mult": "",
        "Subdiv_num": "1",
        "Subdiv_pos": "",
        "Subdiv_titre": "",
        "Subdiv_type": "article",
        "Gouvernemental": "False",
    }


def test_write_csv_sous_amendement(
    lecture_senat, article1, article1av, article7bis, tmpdir
):
    from zam_repondeur.writer import write_csv
    from zam_repondeur.models import DBSession, Amendement

    filename = str(tmpdir.join("test.csv"))

    with transaction.manager:
        amendement = Amendement(
            lecture=lecture_senat,
            article=article1,
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
                article=article1av,
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
                article=article7bis,
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
                article=article1,
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
                article=article1,
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
        nb_rows = write_csv("Titre", amendements, filename, request={})

    with open(filename, "r", encoding="utf-8") as f_:
        lines = f_.read().splitlines()
    headers, *rows = lines

    assert len(rows) == nb_rows == 5

    assert _csv_row_to_dict(headers, rows[-1]) == {
        "Chambre": "senat",
        "Session": "2017-2018",
        "Num_texte": "63",
        "Organe": "PO78718",
        "Subdiv_type": "article",
        "Subdiv_num": "1",
        "Subdiv_mult": "",
        "Subdiv_pos": "",
        "Subdiv_titre": "",
        "Alinéa": "",
        "Nº amdt": "596",
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
        "Dispositif": "grault",
        "Corps amdt": "corge",
        "Exposé amdt": "",
        "Avis du Gouvernement": "",
        "Objet amdt": "",
        "Réponse": "",
        "Gouvernemental": "False",
        "Pk": "000596",
        "Commentaires": "",
    }
