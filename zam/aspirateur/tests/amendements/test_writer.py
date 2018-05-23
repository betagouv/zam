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


def test_write_csv(tmpdir):
    from zam_aspirateur.amendements.models import Amendement
    from zam_aspirateur.amendements.writer import write_csv

    filename = str(tmpdir.join('test.csv'))

    amendements = [
        Amendement(
            article="1",
            alinea="",
            num="42",
            auteur="M. DUPONT",
            matricule="000000",
        ),
    ]

    nb_rows = write_csv(amendements, filename)

    with open(filename, 'r', encoding='utf-8') as f_:
        lines = f_.read().splitlines()
    header, *rows = lines
    assert header == ";".join(FIELDS)

    assert len(rows) == nb_rows == 1

    assert rows[0] == "1;;42;M. DUPONT;000000;;;;;;;"
