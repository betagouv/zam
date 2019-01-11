import transaction


def test_space_empty(app, lecture_an, amendements_an, team_zam, user_david):
    resp = app.get(f"/lectures/an.15.269.PO717460/espaces/moi", user=user_david.email)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"
    assert "Vous n’avez pour l’instant aucun amendement attribué" in resp.text
    assert "Article 1 - Nº&nbsp;<strong>666</strong>" not in resp.text
    assert "Article 1 - Nº&nbsp;<strong>999</strong>" not in resp.text


def test_space_with_one_team(app, lecture_an, amendements_an, team_zam, user_david):
    from zam_repondeur.models import DBSession, Team

    with transaction.manager:
        team_zoom = Team.create(name="Zoom")
        # The team is not added to user_david.
        user_david.teams.append(team_zam)
        DBSession.add(user_david)
        amendements_an[0].user_content.affectation = team_zam.name
        amendements_an[1].user_content.affectation = team_zoom.name
        DBSession.add_all(amendements_an)

    resp = app.get(f"/lectures/an.15.269.PO717460/espaces/moi", user=user_david.email)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"
    assert "Vous n’avez pour l’instant aucun amendement attribué" not in resp.text
    assert "Article 1 - Nº&nbsp;<strong>666</strong>" in resp.text
    assert "Article 1 - Nº&nbsp;<strong>999</strong>" not in resp.text


def test_space_with_two_teams(app, lecture_an, amendements_an, team_zam, user_david):
    from zam_repondeur.models import DBSession, Team

    with transaction.manager:
        team_zoom = Team.create(name="Zoom")
        user_david.teams.append(team_zam)
        user_david.teams.append(team_zoom)
        DBSession.add(user_david)
        amendements_an[0].user_content.affectation = team_zam.name
        amendements_an[1].user_content.affectation = team_zoom.name
        DBSession.add_all(amendements_an)

    resp = app.get(f"/lectures/an.15.269.PO717460/espaces/moi", user=user_david.email)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"
    assert "Vous n’avez pour l’instant aucun amendement attribué" not in resp.text
    assert "Article 1 - Nº&nbsp;<strong>666</strong>" in resp.text
    assert "Article 1 - Nº&nbsp;<strong>999</strong>" in resp.text
