import transaction


def test_add_team(app):
    from zam_repondeur.models import DBSession, Team, User

    resp = app.get("/equipe/rejoindre", user="jane.doe@example.com")
    assert resp.status_code == 200
    resp.forms["add-team"]["name"] = " Bureau 5B "
    resp = resp.forms["add-team"].submit().maybe_follow()
    assert "Équipe « Bureau 5B » créée avec succès." in resp.text
    bureau_5b = DBSession.query(Team).filter_by(name="Bureau 5B").first()
    assert bureau_5b
    jane = DBSession.query(User).filter_by(email="jane.doe@example.com").one()
    assert bureau_5b in jane.teams


def test_add_existing_team(app, team_zam):
    from zam_repondeur.models import DBSession, Team, User

    with transaction.manager:
        DBSession.add(team_zam)

    resp = app.get("/equipe/rejoindre", user="jane.doe@example.com")
    assert resp.status_code == 200
    resp.forms["add-team"]["name"] = "Zam"
    resp = resp.forms["add-team"].submit().maybe_follow()
    assert "Équipe « Zam » rejointe avec succès." in resp.text
    assert len(DBSession.query(Team).filter_by(name="Zam").all()) == 1
    jane = DBSession.query(User).filter_by(email="jane.doe@example.com").one()
    assert jane.teams[0].name == "Zam"


def test_add_already_member_of_team(app, team_zam, user_david):
    from zam_repondeur.models import DBSession, Team, User

    with transaction.manager:
        user_david.teams.append(team_zam)
        DBSession.add(user_david)

    resp = app.get("/equipe/rejoindre", user="david@example.com")
    assert resp.status_code == 200
    resp.forms["add-team"]["name"] = "Zam"
    resp = resp.forms["add-team"].submit().maybe_follow()
    assert "Vous êtes déjà membre de cette équipe !" in resp.text
    assert len(DBSession.query(Team).filter_by(name="Zam").all()) == 1
    david = DBSession.query(User).filter_by(email="david@example.com").one()
    assert len(david.teams) == 1
    assert david.teams[0].name == "Zam"


def test_join_team(app, team_zam, user_david):
    from zam_repondeur.models import DBSession, Team, User

    with transaction.manager:
        DBSession.add(team_zam)

    resp = app.get("/equipe/rejoindre", user="david@example.com")
    assert resp.status_code == 200
    resp.forms["join-team"]["name"] = "Zam"
    resp = resp.forms["join-team"].submit().maybe_follow()
    assert "Équipe « Zam » rejointe avec succès." in resp.text
    assert len(DBSession.query(Team).filter_by(name="Zam").all()) == 1
    david = DBSession.query(User).filter_by(email="david@example.com").one()
    assert len(david.teams) == 1
    assert david.teams[0].name == "Zam"


def test_join_already_member_of_team(app, team_zam, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        user_david.teams.append(team_zam)
        DBSession.add(user_david)

    resp = app.get("/equipe/rejoindre", user="david@example.com")
    assert resp.status_code == 200
    assert resp.forms["join-team"]["name"].options == [
        ("Zam", False, "Zam (déjà membre)")
    ]
