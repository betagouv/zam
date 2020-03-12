def test_home_redirects_to_conseils(app, user_david):
    resp = app.get("/", user=user_david)
    assert resp.status_code == 302
    assert resp.location == "https://zam.test/conseils/"
