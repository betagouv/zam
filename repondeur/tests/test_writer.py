import json

import pytest


@pytest.fixture
def amendements():
    from zam_repondeur.fetch.models import Amendement

    return [
        Amendement(
            chambre="senat",
            session="2017-2018",
            num_texte=63,
            organe="PO78718",
            subdiv_type="article",
            subdiv_num="1",
            alinea="",
            num=42,
            auteur="M. DUPONT",
            groupe="RDSE",
            matricule="000000",
            dispositif="<p>L'article 1 est supprimé.</p>",
            objet="<p>Cet article va à l'encontre du principe d'égalité.</p>",
            resume="Suppression de l'article",
        ),
        Amendement(
            chambre="senat",
            session="2017-2018",
            num_texte=63,
            organe="PO78718",
            subdiv_type="article",
            subdiv_num="1",
            subdiv_pos="avant",
            alinea="",
            num=57,
            auteur="M. DURAND",
            groupe="Les Républicains",
            matricule="000001",
            objet="baz",
            dispositif="qux",
        ),
        Amendement(
            chambre="senat",
            session="2017-2018",
            num_texte=63,
            organe="PO78718",
            subdiv_type="article",
            subdiv_num="7",
            subdiv_mult="bis",
            alinea="",
            num=21,
            auteur="M. MARTIN",
            groupe=None,
            matricule="000002",
            objet="quux",
            dispositif="quuz",
        ),
        Amendement(
            chambre="senat",
            session="2017-2018",
            num_texte=63,
            organe="PO78718",
            subdiv_type="article",
            subdiv_num="1",
            alinea="",
            num=43,
            auteur="M. JEAN",
            groupe="Les Indépendants",
            matricule="000003",
            objet="corge",
            dispositif="grault",
        ),
        Amendement(
            chambre="senat",
            session="2017-2018",
            num_texte=63,
            organe="PO78718",
            subdiv_type="article",
            subdiv_num="1",
            alinea="",
            num=596,
            rectif=1,
            parent_num=229,
            parent_rectif=1,
            auteur="M. JEAN",
            groupe="Les Indépendants",
            matricule="000003",
            objet="corge",
            dispositif="grault",
        ),
    ]


def _csv_row_to_dict(headers, row):
    return dict(zip(headers.split(";"), row.split(";")))


def test_write_csv(amendements, tmpdir):
    from zam_repondeur.writer import write_csv

    filename = str(tmpdir.join("test.csv"))

    nb_rows = write_csv("Titre", amendements, filename, request={})

    with open(filename, "r", encoding="utf-8") as f_:
        lines = f_.read().splitlines()
    headers, *rows = lines

    assert len(rows) == nb_rows == 5

    assert _csv_row_to_dict(headers, rows[0]) == {
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
        "Nº amdt parent": "",
        "Rectif parent": "",
        "Nº amdt": "42",
        "Objet amdt": "",
        "Organe": "PO78718",
        "Position": "",
        "Rectif": "0",
        "Réponse": "",
        "Session": "2017-2018",
        "Sort": "",
        "Subdiv_mult": "",
        "Subdiv_num": "1",
        "Subdiv_pos": "",
        "Subdiv_titre": "",
        "Subdiv_type": "article",
    }


def test_write_csv_sous_amendement(amendements, tmpdir):
    from zam_repondeur.writer import write_csv

    filename = str(tmpdir.join("test.csv"))

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
        "Nº amdt parent": "229",
        "Rectif parent": "1",
        "Dispositif": "grault",
        "Corps amdt": "corge",
        "Exposé amdt": "",
        "Avis du Gouvernement": "",
        "Objet amdt": "",
        "Réponse": "",
        "Commentaires": "",
    }


def test_write_json_for_viewer(amendements, tmpdir):
    from zam_repondeur.writer import write_json_for_viewer

    TITLE = "Projet Loi de Financement de la Sécurité Sociale 2018"

    filename = str(tmpdir.join("test.json"))

    write_json_for_viewer(1, TITLE, amendements, filename)

    with open(filename, "r", encoding="utf-8") as f_:
        data = json.load(f_)

    assert data == [
        {
            "idProjet": 1,
            "libelle": "Projet Loi de Financement de la Sécurité Sociale 2018",
            "list": [
                {
                    "id": 1,
                    "pk": "article-1",
                    "etat": "",
                    "multiplicatif": "",
                    "titre": "TODO",
                    "jaune": "jaune-1.pdf",
                    "document": "article-1.pdf",
                    "amendements": [
                        {
                            "id": 42,
                            "rectif": "",
                            "pk": "000042",
                            "etat": "",
                            "gouvernemental": False,
                            "auteur": "M. DUPONT",
                            "groupe": {"libelle": "RDSE", "couleur": "#a38ebc"},
                            "document": "000042-00.pdf",
                            "dispositif": "<p>L'article 1 est supprimé.</p>",
                            "objet": "<p>Cet article va à l'encontre du principe d'égalité.</p>",  # noqa
                            "resume": "Suppression de l'article",
                            "parent_num": "",
                            "parent_rectif": "",
                        },
                        {
                            "id": 43,
                            "rectif": "",
                            "pk": "000043",
                            "etat": "",
                            "gouvernemental": False,
                            "auteur": "M. JEAN",
                            "groupe": {
                                "libelle": "Les Indépendants",
                                "couleur": "#30bfe9",
                            },
                            "document": "000043-00.pdf",
                            "dispositif": "grault",
                            "objet": "corge",
                            "resume": "",
                            "parent_num": "",
                            "parent_rectif": "",
                        },
                        {
                            "id": 596,
                            "rectif": 1,
                            "pk": "000596",
                            "etat": "",
                            "gouvernemental": False,
                            "auteur": "M. JEAN",
                            "groupe": {
                                "libelle": "Les Indépendants",
                                "couleur": "#30bfe9",
                            },
                            "document": "000596-00.pdf",
                            "dispositif": "grault",
                            "objet": "corge",
                            "resume": "",
                            "parent_num": 229,
                            "parent_rectif": 1,
                        },
                    ],
                },
                {
                    "id": 1,
                    "pk": "article-1av",
                    "etat": "av",
                    "multiplicatif": "",
                    "titre": "TODO",
                    "jaune": "jaune-1av.pdf",
                    "document": "article-1av.pdf",
                    "amendements": [
                        {
                            "id": 57,
                            "rectif": "",
                            "pk": "000057",
                            "etat": "",
                            "gouvernemental": False,
                            "auteur": "M. DURAND",
                            "groupe": {
                                "libelle": "Les Républicains",
                                "couleur": "#2011e8",
                            },
                            "document": "000057-00.pdf",
                            "dispositif": "qux",
                            "objet": "baz",
                            "resume": "",
                            "parent_num": "",
                            "parent_rectif": "",
                        }
                    ],
                },
                {
                    "id": 7,
                    "pk": "article-7bis",
                    "etat": "",
                    "multiplicatif": "bis",
                    "titre": "TODO",
                    "jaune": "jaune-7bis.pdf",
                    "document": "article-7bis.pdf",
                    "amendements": [
                        {
                            "id": 21,
                            "rectif": "",
                            "pk": "000021",
                            "etat": "",
                            "gouvernemental": False,
                            "auteur": "M. MARTIN",
                            "groupe": {"libelle": "", "couleur": "#ffffff"},
                            "document": "000021-00.pdf",
                            "dispositif": "quuz",
                            "objet": "quux",
                            "resume": "",
                            "parent_num": "",
                            "parent_rectif": "",
                        }
                    ],
                },
            ],
        }
    ]
