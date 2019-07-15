from datetime import datetime

import transaction


class TestDossiersLinkInNavbar:
    def test_link_in_navbar_if_at_least_one_dossier_activated(
        self, app, lecture_an, user_david
    ):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            lecture_an.dossier.activated_at = datetime.utcnow()
            DBSession.add(lecture_an)

        resp = app.get("/dossiers/", user=user_david)
        assert 'title="Aller à la liste des dossiers">Dossiers</a></li>' in resp.text

    def test_no_link_in_navbar_if_one_dossier_not_activated(
        self, app, lecture_an, user_david
    ):
        assert lecture_an.dossier.activated_at is None

        resp = app.get("/dossiers/", user=user_david)
        assert (
            'title="Aller à la liste des dossiers">Dossiers</a></li>' not in resp.text
        )

    def test_no_link_in_navbar_if_no_dossier(self, app, user_david):
        resp = app.get("/dossiers/", user=user_david)
        assert (
            'title="Aller à la liste des dossiers">Dossiers</a></li>' not in resp.text
        )


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

    assert len(resp.parser.css("#mes-zams .dossier")) == 1


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

    assert len(resp.parser.css("#mes-zams .dossier")) == 0

    assert "Vous ne participez à aucun dossier législatif pour l’instant." in resp.text
