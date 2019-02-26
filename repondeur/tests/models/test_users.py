def test_user_set_team(team_zam, user_david):
    from zam_repondeur.models import DBSession, User

    user_david.teams.append(team_zam)
    assert DBSession.query(User).first().teams == [team_zam]


def test_user_unset_team(team_zam, user_david):
    from zam_repondeur.models import DBSession, User

    user_david.teams.append(team_zam)
    user_david = DBSession.query(User).first()
    user_david.teams.remove(team_zam)
    assert DBSession.query(User).first().teams == []
