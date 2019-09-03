from datetime import datetime, timedelta

from freezegun import freeze_time


class TestUserActivity:
    def test_user_activity_default(self, users_repository, user_david):
        assert not user_david.is_active

    def test_user_activity_in_use(self, app, user_david, dossier_plfss2018):
        app.get("/dossiers/plfss-2018/", user=user_david)
        assert user_david.is_active

    def test_user_activity_not_anymore_in_use(self, app, user_david, dossier_plfss2018):
        app.get("/dossiers/plfss-2018/", user=user_david)
        assert user_david.is_active

        with freeze_time(datetime.utcnow() + timedelta(minutes=29)):
            assert user_david.is_active

        with freeze_time(datetime.utcnow() + timedelta(minutes=31)):
            assert not user_david.is_active


class TestUserTeamRelationship:
    def test_user_set_team(self, user_david):
        from zam_repondeur.models import DBSession, User, Team

        team_zam = DBSession.query(Team).first()
        assert DBSession.query(User).first().teams == [team_zam]

    def test_user_unset_team(self, user_david):
        from zam_repondeur.models import DBSession, User, Team

        user_david = DBSession.query(User).first()
        team_zam = DBSession.query(Team).first()
        user_david.teams.remove(team_zam)
        assert DBSession.query(User).first().teams == []
