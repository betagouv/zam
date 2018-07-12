from unittest.mock import patch


def test_download_csv(app, dummy_lecture):

    with patch("zam_repondeur.views.lectures.get_amendements") as mock:
        mock.return_value = [], []
        resp = app.get("/lectures/an/15/269/PO717460/amendements/download.csv")

    assert resp.status_code == 200

    assert resp.content_type == "text/csv"

    filename = "amendements-an-15-269-PO717460.csv"
    assert resp.headers["Content-Disposition"] == f"attachment; filename={filename}"


def test_download_csv_bad_request(app):

    resp = app.get(
        "/lectures/bad/15/269/PO717460/amendements/download.csv", expect_errors=True
    )

    assert resp.status_code == 404


def test_download_pdf(app, dummy_lecture):

    with patch("zam_repondeur.views.lectures.get_amendements") as mock:
        mock.return_value = [], []
        resp = app.get("/lectures/an/15/269/PO717460/amendements/download.pdf")

    assert resp.status_code == 200

    assert resp.content_type == "application/pdf"

    filename = "amendements-an-15-269-PO717460.pdf"
    assert resp.headers["Content-Disposition"] == f"attachment; filename={filename}"


def test_download_pdf_bad_request(app):

    resp = app.get(
        "/lectures/bad/15/269/PO717460/amendements/download.pdf", expect_errors=True
    )

    assert resp.status_code == 404


def test_download_xlsx(app, dummy_lecture):

    with patch("zam_repondeur.views.lectures.get_amendements") as mock:
        mock.return_value = [], []
        resp = app.get("/lectures/an/15/269/PO717460/amendements/download.xlsx")

    assert resp.status_code == 200

    content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert resp.content_type == content_type

    filename = "amendements-an-15-269-PO717460.xlsx"
    assert resp.headers["Content-Disposition"] == f"attachment; filename={filename}"


def test_download_xlsx_bad_request(app):

    resp = app.get(
        "/lectures/bad/15/269/PO717460/amendements/download.xlsx", expect_errors=True
    )

    assert resp.status_code == 404
