from datetime import datetime, timedelta

import pytest
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
        from zam_repondeur.models import DBSession, Team, User

        team_zam = DBSession.query(Team).first()
        assert DBSession.query(User).first().teams == [team_zam]

    def test_user_unset_team(self, user_david):
        from zam_repondeur.models import DBSession, Team, User

        user_david = DBSession.query(User).first()
        team_zam = DBSession.query(Team).first()
        user_david.teams.remove(team_zam)
        assert DBSession.query(User).first().teams == []


class TestAllowedEmailPattern:
    @pytest.mark.parametrize(
        "pattern,email",
        [
            ("*", "test@example.org"),
            ("*@example.org", "test@example.org"),
            ("*@example.org", "john.doe@example.org"),
            ("john.doe@example.org", "john.doe@example.org"),
        ],
    )
    def test_pattern_allows_email(self, pattern, email):
        from zam_repondeur.models.users import AllowedEmailPattern

        p = AllowedEmailPattern(pattern=pattern)
        assert p.is_allowed(email)

    @pytest.mark.parametrize(
        "pattern,email",
        [
            ("", "test@example.org"),
            ("*@example.org", "test@otherdomain.org"),
            ("*@example.org", "test@subdomain.example.org"),
            ("john.doe@example.org", "someone.else@example.org"),
        ],
    )
    def test_pattern_does_not_allow_email(self, pattern, email):
        from zam_repondeur.models.users import AllowedEmailPattern

        p = AllowedEmailPattern(pattern=pattern)
        assert not p.is_allowed(email)


class TestEmailWellFormed:
    @pytest.mark.parametrize("email", ["test@exemple.gouv.fr"])
    def test_email_is_well_formed(self, email):
        from zam_repondeur.models.users import User

        assert User.email_is_well_formed(email)

    @pytest.mark.parametrize(
        "email", ["", "testexemple.gouv.fr", "nótäscíî@exemple.gouv.fr"]
    )
    def test_email_is_not_well_formed(self, email):
        from zam_repondeur.models.users import User

        assert not User.email_is_well_formed(email)
