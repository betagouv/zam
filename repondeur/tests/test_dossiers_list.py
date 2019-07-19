def test_team_member_can_see_owned_dossier(app, lecture_an, user_david):
    resp = app.get("/dossiers/", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert len(resp.parser.css(".dossier h3 a")) == 1


def test_sgg_member_can_see_all_dossiers(app, lecture_an, user_sgg):
    resp = app.get("/dossiers/", user=user_sgg)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert len(resp.parser.css(".dossier h3 a")) == 1


def test_non_team_member_cannot_see_their_dossier(app, lecture_an, user_ronan):
    resp = app.get("/dossiers/", user=user_ronan)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert len(resp.parser.css(".dossier h3 a")) == 0

    assert "Vous ne participez à aucun dossier législatif pour l’instant." in resp.text
