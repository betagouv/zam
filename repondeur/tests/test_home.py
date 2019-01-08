def test_home_redirects_to_lectures(app):
    resp = app.get("/", user="user@example.com")
    assert resp.status_code == 302
    assert resp.location == "https://zam.test/lectures/"
