import pytest


@pytest.mark.parametrize(
    "format_,content_type",
    [
        ("pdf", "application/pdf"),
        ("xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    ],
)
def test_download(app, lecture_an, amendements_an, format_, content_type, user_david):

    resp = app.get(
        "/lectures/an.15.269.PO717460/download_amendements",
        {"format": format_},
        user=user_david,
    )

    assert resp.status_code == 200
    assert resp.content_type == content_type
    assert (
        resp.headers["Content-Disposition"]
        == f"attachment; filename=lecture-an-269-PO717460.{format_}"
    )


def test_download_bad_format(app, lecture_an, user_david):
    resp = app.get(
        "/lectures/an.15.269.PO717460/download_amendements",
        {"format": "docx"},
        user=user_david,
        expect_errors=True,
    )

    assert resp.status_code == 400
    assert resp.content_type == "text/plain"
    assert 'Invalid value "docx" for "format" param' in resp.text


def test_download_multiple_amendements(app, lecture_an, amendements_an, user_david):
    resp = app.get(
        "/lectures/an.15.269.PO717460/export_pdf?nums=666&nums=999", user=user_david
    )
    assert resp.status_code == 200
    assert resp.content_type == "application/pdf"
    assert (
        resp.headers["Content-Disposition"]
        == f"attachment; filename=amendements-666,999-an-269-PO717460.pdf"
    )
