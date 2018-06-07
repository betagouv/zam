def test_get_list_empty(app):

    resp = app.get("/lectures/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert "Aucune lecture pour l'instant." in resp.text


def test_get_list_not_empty(app, dummy_lecture):

    resp = app.get("/lectures/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert "Sénat, session 2017-2018, texte nº 63" in resp.text
