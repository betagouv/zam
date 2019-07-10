import transaction


def test_team_member_can_access_owned_dossier(
    app, dossier_plfss2018, team_zam, user_david
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        dossier_plfss2018.owned_by_team = team_zam
        user_david.teams.append(team_zam)
        DBSession.add(team_zam)

    resp = app.get(f"/dossiers/plfss-2018/", user=user_david)

    assert resp.status_code == 200


def test_non_team_member_cannot_access_owned_dossier(
    app, dossier_plfss2018, team_zam, user_david
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        dossier_plfss2018.owned_by_team = team_zam
        DBSession.add(team_zam)

    resp = app.get(f"/dossiers/plfss-2018/", user=user_david)

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/"

    resp = resp.maybe_follow()

    assert "L’accès à ce dossier est réservé aux personnes autorisées." in resp.text
