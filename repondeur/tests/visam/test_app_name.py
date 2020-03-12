def test_app_name_is_visam(app):
    resp = app.get("/deconnecte")
    assert resp.status_code == 200
    assert resp.parser.css("h1")[0].text().strip() == "Déconnexion de Visam réussie"
