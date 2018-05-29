def test_get_list(app):

    resp = app.get("/textes/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"
