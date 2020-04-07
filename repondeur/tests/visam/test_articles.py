def test_article_preview(
    app, conseil_ccfp, lecture_conseil_ccfp, articles_conseil_ccfp, user_ccfp
):
    article = articles_conseil_ccfp[0]
    resp = app.get(
        (
            f"/conseils/{conseil_ccfp.slug}"
            f"/textes/{lecture_conseil_ccfp.dossier.slug}"
            f"/articles/{article.url_key}/preview"
        ),
        user=user_ccfp,
    )

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert "<dt>001</dt>" in resp.text
    assert "<dd>Contenu article 1</dd>" in resp.text
