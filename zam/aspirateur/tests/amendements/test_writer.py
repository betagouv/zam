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
            matricule="000000",
        ),
        Amendement(
            article="Article 1",
            alinea="",
            num="57",
            auteur="M. DURAND",
            matricule="000001",
        ),
        Amendement(
            article="Article 7 bis",
            alinea="",
            num="21",
            auteur="M. MARTIN",
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

    assert rows[0] == "Article 1;;42;M. DUPONT;000000;;;;;;;"
