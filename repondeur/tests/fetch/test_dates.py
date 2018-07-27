from datetime import date


def test_parse_date_short():
    from zam_repondeur.fetch.dates import parse_date

    assert parse_date("2017-11-13") == date(2017, 11, 13)


def test_parse_date_long():
    from zam_repondeur.fetch.dates import parse_date

    assert parse_date("2017-10-11T00:00:00.000+02:00") == date(2017, 10, 11)


def test_parse_date_empty_string():
    from zam_repondeur.fetch.dates import parse_date

    assert parse_date("") is None
