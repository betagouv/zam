def test_get_lecture(app, dummy_lecture):
    resp = app.get("http://localhost/lectures/senat/2017-2018/63/")
    assert resp.status_code == 200


def test_get_lecture_not_found(app):
    resp = app.get("http://localhost/lectures/senat/2017-2018/1/", expect_errors=True)
    assert resp.status_code == 404
