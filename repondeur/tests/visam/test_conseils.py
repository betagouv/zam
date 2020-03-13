def test_conseils_empty(app, user_david):
    resp = app.get("/conseils/", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert "Aucun conseil pour l’instant." in resp.text


def test_conseils(app, conseil_ccfp, user_david):
    resp = app.get("/conseils/", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert len(resp.parser.css(".conseil nav a")) == 1
