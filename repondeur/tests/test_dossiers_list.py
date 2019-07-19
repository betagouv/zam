from datetime import datetime

import transaction


def test_team_member_can_see_owned_and_activated_dossier(
    app, lecture_an, team_zam, user_david
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        lecture_an.dossier.activated_at = datetime.utcnow()
        lecture_an.dossier.owned_by_team = team_zam
        DBSession.add(user_david)
        user_david.teams.append(team_zam)
        DBSession.add(team_zam)

    resp = app.get("/dossiers/", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert len(resp.parser.css(".dossier h3 a")) == 1


def test_non_team_member_cannot_see_owned_dossier_even_if_activated(
    app, lecture_an, team_zam, user_david
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        lecture_an.dossier.activated_at = datetime.utcnow()
        lecture_an.dossier.owned_by_team = team_zam
        DBSession.add(team_zam)

    resp = app.get("/dossiers/", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert len(resp.parser.css(".dossier h3 a")) == 0

    assert "Vous ne participez à aucun dossier législatif pour l’instant." in resp.text
