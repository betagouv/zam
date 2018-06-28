from unittest.mock import patch


def test_download_csv(app):

    with patch("zam_repondeur.views.lectures.get_amendements") as mock:
        mock.return_value = [], []
        resp = app.get("/lectures/senat/2017-2018/63/amendements/download.csv")

    assert resp.status_code == 200

    assert resp.content_type == "text/csv"

    filename = "amendements-senat-2017-2018-63.csv"
    assert resp.headers["Content-Disposition"] == f"attachment; filename={filename}"


def test_download_csv_bad_request(app):

    resp = app.get(
        "/lectures/bad/2017-2018/63/amendements/download.csv", expect_errors=True
    )

    assert resp.status_code == 400
    assert resp.content_type == "text/plain"
    assert 'Invalid value "bad" for "chambre" param' in resp.text


def test_download_xlsx(app):

    with patch("zam_repondeur.views.lectures.get_amendements") as mock:
        mock.return_value = [], []
        resp = app.get("/lectures/senat/2017-2018/63/amendements/download.xlsx")

    assert resp.status_code == 200

    content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert resp.content_type == content_type

    filename = "amendements-senat-2017-2018-63.xlsx"
    assert resp.headers["Content-Disposition"] == f"attachment; filename={filename}"


def test_download_xlsx_bad_request(app):

    resp = app.get(
        "/lectures/bad/2017-2018/63/amendements/download.xlsx", expect_errors=True
    )

    assert resp.status_code == 400
    assert resp.content_type == "text/plain"
    assert 'Invalid value "bad" for "chambre" param' in resp.text
