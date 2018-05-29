def test_home(app):
    resp = app.get("/")
    assert resp.status_code == 200
    assert resp.content_type == "text/html"
    assert "Hello world" in resp.text
