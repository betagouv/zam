# fmt: off
import json

import pytest


@pytest.fixture
def amendements():
    from zam_aspirateur.amendements.models import Amendement
    return [
        Amendement(
            subdiv_type="article",
            subdiv_num="1",
            alinea="",
            num="42",
            auteur="M. DUPONT",
            groupe="RDSE",
            matricule="000000",
            objet="foo",
            dispositif="bar",
        ),
        Amendement(
            subdiv_type="article",
            subdiv_num="1",
            subdiv_pos="avant",
            alinea="",
            num="57",
            auteur="M. DURAND",
            groupe="Les Républicains",
            matricule="000001",
            objet="baz",
            dispositif="qux",
        ),
        Amendement(
            subdiv_type="article",
            subdiv_num="7",
            subdiv_mult="bis",
            alinea="",
            num="21",
            auteur="M. MARTIN",
            groupe=None,
            matricule="000002",
            objet="quux",
            dispositif="quuz",
        ),
        Amendement(
            subdiv_type="article",
            subdiv_num="1",
            alinea="",
            num="43",
            auteur="M. JEAN",
            groupe="Les Indépendants",
            matricule="000003",
            objet="corge",
            dispositif="grault",
        ),
    ]


FIELDS = [
    "subdiv_type",
    "subdiv_num",
    "subdiv_mult",
    "subdiv_pos",
    "alinea",
    "num",
    "rectif",
    "auteur",
    "matricule",
    "groupe",
    "date_depot",
    "sort",
    "discussion_commune",
    "identique",
    "dispositif",
    "objet",
    "avis",
    "observations",
    "reponse",
]


def test_write_csv(amendements, tmpdir):
    from zam_aspirateur.amendements.writer import write_csv

    filename = str(tmpdir.join('test.csv'))

    nb_rows = write_csv(amendements, filename)

    with open(filename, 'r', encoding='utf-8') as f_:
        lines = f_.read().splitlines()
    header, *rows = lines
    assert header == ";".join(FIELDS)

    assert len(rows) == nb_rows == 4

    assert rows[0] == "article;1;;;;42;0;M. DUPONT;000000;RDSE;;;;;bar;foo;;;"


def test_write_json_for_viewer(amendements, tmpdir):
    from zam_aspirateur.amendements.writer import write_json_for_viewer

    TITLE = "Projet Loi de Financement de la Sécurité Sociale 2018"

    filename = str(tmpdir.join('test.json'))

    write_json_for_viewer(1, TITLE, amendements, filename)

    with open(filename, 'r', encoding='utf-8') as f_:
        data = json.load(f_)

    assert data == [
        {
            'idProjet': 1,
            'libelle': 'Projet Loi de Financement de la Sécurité Sociale 2018',
            'list': [
                {
                    'id': 1,
                    'pk': 'article-1',
                    'etat': '',
                    'multiplicatif': '',
                    'titre': 'TODO',
                    'jaune': 'jaune-1.pdf',
                    'document': 'article-1.pdf',
                    'amendements': [
                        {
                            'id': 42,
                            'pk': '000042',
                            'etat': '',
                            'gouvernemental': False,
                            'auteur': 'M. DUPONT',
                            "groupe": {
                                "libelle": "RDSE",
                                "couleur": "#a38ebc"
                            },
                            'document': '000042-00.pdf',
                            'objet': 'foo',
                            'dispositif': 'bar'
                        },
                        {
                            'id': 43,
                            'pk': '000043',
                            'etat': '',
                            'gouvernemental': False,
                            'auteur': 'M. JEAN',
                            "groupe": {
                                "libelle": "Les Indépendants",
                                "couleur": "#30bfe9"
                            },
                            'document': '000043-00.pdf',
                            'objet': 'corge',
                            'dispositif': 'grault',
                        },
                    ],
                },
                {
                    'id': 1,
                    'pk': 'article-1av',
                    'etat': 'av',
                    'multiplicatif': '',
                    'titre': 'TODO',
                    'jaune': 'jaune-1av.pdf',
                    'document': 'article-1av.pdf',
                    'amendements': [
                        {
                            'id': 57,
                            'pk': '000057',
                            'etat': '',
                            'gouvernemental': False,
                            'auteur': 'M. DURAND',
                            "groupe": {
                                "libelle": "Les Républicains",
                                "couleur": "#2011e8"
                            },
                            'document': '000057-00.pdf',
                            'objet': 'baz',
                            'dispositif': 'qux',
                        },
                    ],
                },
                {
                    'id': 7,
                    'pk': 'article-7bis',
                    'etat': '',
                    'multiplicatif': 'bis',
                    'titre': 'TODO',
                    'jaune': 'jaune-7bis.pdf',
                    'document': 'article-7bis.pdf',
                    'amendements': [
                        {
                            'id': 21,
                            'pk': '000021',
                            'etat': '',
                            'gouvernemental': False,
                            'auteur': 'M. MARTIN',
                            "groupe": {
                                "libelle": "",
                                "couleur": "#ffffff"
                            },
                            'document': '000021-00.pdf',
                            'objet': 'quux',
                            'dispositif': 'quuz',
                        },
                    ],
                }
            ],
        },
    ]
