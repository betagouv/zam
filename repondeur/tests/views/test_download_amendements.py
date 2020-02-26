import pytest
import transaction


@pytest.mark.parametrize(
    "format_,content_type",
    [
        ("pdf", "application/pdf"),
        ("xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    ],
)
def test_download(app, lecture_an, amendements_an, format_, content_type, user_david):

    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/download_amendements",
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
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/download_amendements",
        {"format": "docx"},
        user=user_david,
        expect_errors=True,
    )

    assert resp.status_code == 400
    assert resp.content_type == "text/plain"
    assert 'Invalid value "docx" for "format" param' in resp.text


def test_download_pdf_multiple_amendements(
    app, lecture_an, article1_an, amendements_an, user_david
):
    resp = app.get(
        (
            f"/dossiers/plfss-2018/lectures/an.15.269.PO717460/export_pdf"
            f"?article={article1_an.url_key}&n=666&n=999"
        ),
        user=user_david,
    )
    assert resp.status_code == 200
    assert resp.content_type == "application/pdf"
    assert (
        resp.headers["Content-Disposition"]
        == f"attachment; filename=an-269-PO717460-article1-amendements-666_999.pdf"
    )


def test_download_pdf_multiple_amendements_multiple_articles(
    app, lecture_an, article7bis_an, amendements_an, user_david
):
    from zam_repondeur.models import Amendement

    with transaction.manager:
        Amendement.create(lecture=lecture_an, article=article7bis_an, num=777)

    resp = app.get(
        (
            f"/dossiers/plfss-2018/lectures/an.15.269.PO717460/export_pdf"
            f"?article=all&n=666&n=777"
        ),
        user=user_david,
    )
    assert resp.status_code == 200
    assert resp.content_type == "application/pdf"
    assert (
        resp.headers["Content-Disposition"]
        == f"attachment; filename=an-269-PO717460-amendements-666_777.pdf"
    )


def test_download_pdf_lots_of_amendements(app, lecture_an, article1_an, user_david):
    from zam_repondeur.models import Amendement

    nb_amendements = 11
    with transaction.manager:
        for i in range(nb_amendements):
            Amendement.create(lecture=lecture_an, article=article1_an, num=i + 1)

    params = "&".join(f"n={i+1}" for i in range(nb_amendements))
    resp = app.get(
        (
            f"/dossiers/plfss-2018/lectures/an.15.269.PO717460/export_pdf"
            f"?article={article1_an.url_key}&{params}"
        ),
        user=user_david,
    )
    assert resp.content_type == "application/pdf"
    assert (
        resp.headers["Content-Disposition"]
        == f"attachment; filename=an-269-PO717460-article1-11amendements-1etc.pdf"
    )


def test_download_pdf_multiple_amendements_same_batch(
    app, lecture_an, article1_an, amendements_an_batch, user_david
):
    resp = app.get(
        (
            f"/dossiers/plfss-2018/lectures/an.15.269.PO717460/export_pdf"
            f"?article={article1_an.url_key}&n=666"
        ),
        user=user_david,
    )
    assert resp.status_code == 200
    assert resp.content_type == "application/pdf"
    assert (
        resp.headers["Content-Disposition"]
        == f"attachment; filename=an-269-PO717460-article1-amendements-666_999.pdf"
    )


def test_download_xlsx_multiple_amendements(
    app, lecture_an, article1_an, amendements_an, user_david
):
    resp = app.get(
        (
            f"/dossiers/plfss-2018/lectures/an.15.269.PO717460/export_xlsx"
            f"?article={article1_an.url_key}&n=666&n=999"
        ),
        user=user_david,
    )
    assert resp.status_code == 200
    assert (
        resp.content_type
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert (
        resp.headers["Content-Disposition"]
        == f"attachment; filename=an-269-PO717460-article1-amendements-666_999.xlsx"
    )


def test_download_xlsx_multiple_amendements_multiple_articles(
    app, lecture_an, article7bis_an, amendements_an, user_david
):
    from zam_repondeur.models import Amendement

    with transaction.manager:
        Amendement.create(lecture=lecture_an, article=article7bis_an, num=777)

    resp = app.get(
        (
            f"/dossiers/plfss-2018/lectures/an.15.269.PO717460/export_xlsx"
            f"?article=all&n=666&n=777"
        ),
        user=user_david,
    )
    assert resp.status_code == 200
    assert (
        resp.content_type
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert (
        resp.headers["Content-Disposition"]
        == f"attachment; filename=an-269-PO717460-amendements-666_777.xlsx"
    )


def test_download_xlsx_lots_of_amendements(app, lecture_an, article1_an, user_david):
    from zam_repondeur.models import Amendement

    nb_amendements = 11
    with transaction.manager:
        for i in range(nb_amendements):
            Amendement.create(lecture=lecture_an, article=article1_an, num=i + 1)

    params = "&".join(f"n={i+1}" for i in range(nb_amendements))
    resp = app.get(
        (
            f"/dossiers/plfss-2018/lectures/an.15.269.PO717460/export_xlsx"
            f"?article={article1_an.url_key}&{params}"
        ),
        user=user_david,
    )
    assert resp.status_code == 200
    assert (
        resp.content_type
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert (
        resp.headers["Content-Disposition"]
        == f"attachment; filename=an-269-PO717460-article1-11amendements-1etc.xlsx"
    )


def test_download_xlsx_multiple_amendements_same_batch(
    app, lecture_an, article1_an, amendements_an_batch, user_david
):
    resp = app.get(
        (
            f"/dossiers/plfss-2018/lectures/an.15.269.PO717460/export_xlsx"
            f"?article={article1_an.url_key}&n=666"
        ),
        user=user_david,
    )
    assert resp.status_code == 200
    assert (
        resp.content_type
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert (
        resp.headers["Content-Disposition"]
        == f"attachment; filename=an-269-PO717460-article1-amendements-666_999.xlsx"
    )
