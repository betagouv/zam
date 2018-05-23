import json

import pytest


@pytest.fixture
def amendements():
    from zam_aspirateur.amendements.models import Amendement
    return [
        Amendement(
            article="Article 1",
            alinea="",
            num="42",
            auteur="M. DUPONT",
            groupe="ABC",
            matricule="000000",
        ),
        Amendement(
            article="Article 1",
            alinea="",
            num="57",
            auteur="M. DURAND",
            groupe="DEF",
            matricule="000001",
        ),
        Amendement(
            article="Article 7 bis",
            alinea="",
            num="21",
            auteur="M. MARTIN",
            groupe="GHI",
            matricule="000002",
        ),
    ]


FIELDS = [
    "article",
    "alinea",
    "num",
    "auteur",
    "matricule",
    "groupe",
    "date_depot",
    "sort",
    "discussion_commune",
    "identique",
    "dispositif",
    "objet",
]


def test_write_csv(amendements, tmpdir):
    from zam_aspirateur.amendements.writer import write_csv

    filename = str(tmpdir.join('test.csv'))

    nb_rows = write_csv(amendements, filename)

    with open(filename, 'r', encoding='utf-8') as f_:
        lines = f_.read().splitlines()
    header, *rows = lines
    assert header == ";".join(FIELDS)

    assert len(rows) == nb_rows == 3

    assert rows[0] == "Article 1;;42;M. DUPONT;000000;ABC;;;;;;"


@pytest.mark.parametrize('text,exp_num,exp_mult', [
    ('', None, ''),
    ('Article 1', 1, ''),
    ('Article 8\xa0bis', 8, 'bis'),
    ('art. add. après Article 7', 7, ''),
    ('Article 31 (précédemment examiné)', 31, ''),
])
def test_parse_article(text, exp_num, exp_mult):
    from zam_aspirateur.amendements.writer import _parse_article

    num, mult = _parse_article(text)
    assert (num, mult) == (exp_num, exp_mult)


def test_write_json_for_viewer(amendements, tmpdir):
    from zam_aspirateur.amendements.writer import write_json_for_viewer

    TITLE = "Projet Loi de Financement de la Sécurité Sociale 2018"

    filename = str(tmpdir.join('test.json'))

    write_json_for_viewer(1, TITLE, amendements, filename)

    with open(filename, 'r', encoding='utf-8') as f_:
        data = json.load(f_)

    # print(data)
    # assert False

    assert data == [
        {
            'idProjet': 1,
            'libelle': 'Projet Loi de Financement de la Sécurité Sociale 2018',
            'list': [
                {
                    'idArticle': 1,
                    'etat': '',
                    'multiplicatif': '',
                    'titre': 'TODO',
                    'feuilletJaune': 'jaune-1.pdf',
                    'document': 'article-1.pdf',
                    'amendements': [
                        {
                            'idAmendement': 42,
                            'etat': '',
                            'gouvernemental': False,
                            'auteurs': [{
                                'auteur': 'M. DUPONT',
                                'couleur': '#ffffff',
                            }],
                            "groupesParlementaires": [
                                {
                                    "libelle": "ABC",
                                    "couleur": "#ffffff"
                                }
                            ],
                            "reponse": {
                                "idReponse": 42,
                                "avis": "Défavorable",
                                "presentation": "<p><strong>Consequat ea cupidatat in nostrud.</strong></p>",  # noqa
                                "reponse": "<p>Proident anim cillum ea magna eiusmod enim consectetur nisi sed magna ut id sed ad officia.</p>",  # noqa
                            },
                            'document': '00042-00.pdf',
                            'annexes': [],
                        },
                        {
                            'idAmendement': 57,
                            'etat': '',
                            'gouvernemental': False,
                            'auteurs': [{
                                'auteur': 'M. DURAND',
                                'couleur': '#ffffff',
                            }],
                            "groupesParlementaires": [
                                {
                                    "libelle": "DEF",
                                    "couleur": "#ffffff"
                                }
                            ],
                            "reponse": {
                                "idReponse": 57,
                                "avis": "Défavorable",
                                "presentation": "<p><strong>Consequat ea cupidatat in nostrud.</strong></p>",  # noqa
                                "reponse": "<p>Proident anim cillum ea magna eiusmod enim consectetur nisi sed magna ut id sed ad officia.</p>",  # noqa
                            },
                            'document': '00057-00.pdf',
                            'annexes': [],
                        },
                    ],
                },
                {
                    'idArticle': 7,
                    'etat': '',
                    'multiplicatif': 'bis',
                    'titre': 'TODO',
                    'feuilletJaune': 'jaune-7bis.pdf',
                    'document': 'article-7bis.pdf',
                    'amendements': [
                        {
                            'idAmendement': 21,
                            'etat': '',
                            'gouvernemental': False,
                            'auteurs': [{
                                'auteur': 'M. MARTIN',
                                'couleur': '#ffffff',
                            }],
                            "groupesParlementaires": [
                                {
                                    "libelle": "GHI",
                                    "couleur": "#ffffff"
                                }
                            ],
                            "reponse": {
                                "idReponse": 21,
                                "avis": "Défavorable",
                                "presentation": "<p><strong>Consequat ea cupidatat in nostrud.</strong></p>",  # noqa
                                "reponse": "<p>Proident anim cillum ea magna eiusmod enim consectetur nisi sed magna ut id sed ad officia.</p>",  # noqa
                            },
                            'document': '00021-00.pdf',
                            'annexes': [],
                        },
                    ],
                }
            ],
        },
    ]
