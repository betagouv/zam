def test_article_preview(app, articles_conseil_ccfp, user_david):
    resp = app.get(
        (
            "/dossiers/titre-texte-ccfp"
            "/lectures/ccfp..1.Assembl%C3%A9e%20pl%C3%A9ni%C3%A8re"
            "/articles/article.1../preview"
        ),
        user=user_david,
    )

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert "<dt>001</dt>" in resp.text
    assert "<dd>Contenu article 1</dd>" in resp.text
