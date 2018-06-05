def test_home_redirects_to_lectures(app):
    resp = app.get("/")
    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/"
