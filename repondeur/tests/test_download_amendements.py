from unittest.mock import patch


def test_download_csv(app, lecture_an):

    with patch("zam_repondeur.fetch.get_amendements") as mock:
        mock.return_value = [], []
        resp = app.get(
            "/lectures/an.15.269.PO717460/download_amendements", {"format": "csv"}
        )

    assert resp.status_code == 200

    assert resp.content_type == "text/csv"

    filename = "amendements-an-15-269-PO717460.csv"
    assert resp.headers["Content-Disposition"] == f"attachment; filename={filename}"


def test_download_pdf(app, lecture_an):

    with patch("zam_repondeur.fetch.get_amendements") as mock:
        mock.return_value = [], []
        resp = app.get(
            "/lectures/an.15.269.PO717460/download_amendements", {"format": "pdf"}
        )

    assert resp.status_code == 200

    assert resp.content_type == "application/pdf"

    filename = "amendements-an-15-269-PO717460.pdf"
    assert resp.headers["Content-Disposition"] == f"attachment; filename={filename}"


def test_download_xlsx(app, lecture_an):

    with patch("zam_repondeur.fetch.get_amendements") as mock:
        mock.return_value = [], []
        resp = app.get(
            "/lectures/an.15.269.PO717460/download_amendements", {"format": "xlsx"}
        )

    assert resp.status_code == 200

    content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert resp.content_type == content_type

    filename = "amendements-an-15-269-PO717460.xlsx"
    assert resp.headers["Content-Disposition"] == f"attachment; filename={filename}"


def test_download_bad_format(app, lecture_an):
    resp = app.get(
        "/lectures/an.15.269.PO717460/download_amendements",
        {"format": "docx"},
        expect_errors=True,
    )

    assert resp.status_code == 400
    assert resp.content_type == "text/plain"
    assert 'Invalid value "docx" for "format" param' in resp.text
