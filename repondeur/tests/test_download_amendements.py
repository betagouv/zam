from unittest.mock import patch

import pytest


@pytest.mark.parametrize(
    "format_,content_type",
    [
        ("json", "application/json"),
        ("pdf", "application/pdf"),
        ("xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    ],
)
def test_download(app, lecture_an, format_, content_type):

    with patch("zam_repondeur.fetch.get_amendements") as mock:
        mock.return_value = [], []
        resp = app.get(
            "/lectures/an.15.269.PO717460/download_amendements", {"format": format_}
        )

    assert resp.status_code == 200
    assert resp.content_type == content_type
    assert (
        resp.headers["Content-Disposition"]
        == f"attachment; filename=lecture-an-15-269-PO717460.{format_}"
    )


def test_download_bad_format(app, lecture_an):
    resp = app.get(
        "/lectures/an.15.269.PO717460/download_amendements",
        {"format": "docx"},
        expect_errors=True,
    )

    assert resp.status_code == 400
    assert resp.content_type == "text/plain"
    assert 'Invalid value "docx" for "format" param' in resp.text
