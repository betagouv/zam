FIELDS = [
    "article",
    "alinea",
    "num",
    "auteur",
    "date_depot",
    "sort",
    "discussion_commune",
    "identique",
]


def test_write_csv(tmpdir):
    from writer import write_csv

    filename = str(tmpdir.join('test.csv'))

    write_csv([], filename)

    with open(filename, 'r', encoding='utf-8') as f_:
        data = f_.read()
    assert data == ";".join(FIELDS) + '\n'
