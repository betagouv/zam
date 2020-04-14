def test_article_preview(
    app, seance_ccfp, lecture_seance_ccfp, articles_seance_ccfp, user_ccfp
):
    article = articles_seance_ccfp[0]
    resp = app.get(
        (
            f"/seances/{seance_ccfp.slug}"
            f"/textes/{lecture_seance_ccfp.dossier.slug}"
            f"/articles/{article.url_key}/preview"
        ),
        user=user_ccfp,
    )

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert "<dt>001</dt>" in resp.text
    assert "<dd>Contenu article 1</dd>" in resp.text
