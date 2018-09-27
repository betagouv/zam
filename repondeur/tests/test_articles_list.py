def test_list_lecture_articles(app, lecture_an):
    resp = app.get("http://localhost/lectures/an.15.269.PO717460/articles/")
    assert resp.status_code == 200
