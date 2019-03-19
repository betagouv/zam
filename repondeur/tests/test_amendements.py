import transaction


def test_get_amendements(app, lecture_an, amendements_an):
    resp = app.get("/lectures/an.15.269.PO717460/amendements", user="user@example.com")

    assert resp.status_code == 200
    assert "Dossier de banc" not in resp.text


def test_no_amendements(app, lecture_an):
    resp = app.get("/lectures/an.15.269.PO717460/amendements", user="user@example.com")

    assert resp.status_code == 200
    assert "Dossier de banc" not in resp.text
    assert "Aucun amendement disponible pour l’instant" in resp.text


def test_team_member_can_access_owned_lecture(
    app, lecture_an, team_zam, user_david, amendements_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        lecture_an.owned_by_team = team_zam
        user_david.teams.append(team_zam)
        DBSession.add(team_zam)

    resp = app.get("/lectures/an.15.269.PO717460/amendements", user=user_david.email)

    assert resp.status_code == 200
    assert "Dossier de banc" not in resp.text


def test_non_team_member_cannot_access_owned_lecture(
    app, lecture_an, team_zam, user_david, amendements_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        lecture_an.owned_by_team = team_zam
        DBSession.add(team_zam)

    resp = app.get("/lectures/an.15.269.PO717460/amendements", user=user_david.email)

    assert resp.status_code == 302
    resp = resp.maybe_follow()

    assert "L’accès à cette lecture est réservé aux personnes autorisées." in resp.text


def test_get_amendements_with_avis(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendement = amendements_an[0]
        amendement.user_content.avis = "Favorable"
        DBSession.add(amendement)

    resp = app.get("/lectures/an.15.269.PO717460/amendements", user="user@example.com")

    assert resp.status_code == 200
    assert "Dossier de banc" in resp.text


def test_get_amendements_with_gouvernemental(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendement = amendements_an[0]
        amendement.auteur = "LE GOUVERNEMENT"
        DBSession.add(amendement)

    resp = app.get("/lectures/an.15.269.PO717460/amendements", user="user@example.com")

    assert resp.status_code == 200
    assert "Dossier de banc" in resp.text


def test_get_amendements_order_default(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.user_content.avis = "Favorable"
        DBSession.add_all(amendements_an)

    resp = app.get("/lectures/an.15.269.PO717460/amendements", user="user@example.com")

    assert resp.status_code == 200
    assert "Dossier de banc" in resp.text
    assert [node.text().strip() for node in resp.parser.css("tr td:nth-child(3)")] == [
        "666",
        "999",
    ]


def test_get_amendements_order_abandoned_last(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendements_an[0].sort = "Irrecevable"
        for amendement in amendements_an:
            amendement.user_content.avis = "Favorable"
        DBSession.add_all(amendements_an)

    resp = app.get("/lectures/an.15.269.PO717460/amendements", user="user@example.com")

    assert resp.status_code == 200
    assert "Dossier de banc" in resp.text
    assert [
        " ".join(node.text().strip().split())
        for node in resp.parser.css("tr td:nth-child(3)")
    ] == ["999", "666 Irr."]


def test_get_amendements_not_found_bad_format(app):
    resp = app.get(
        "/lectures/senat.2017-2018.1/amendements",
        user="user@example.com",
        expect_errors=True,
    )
    assert resp.status_code == 404


def test_get_amendements_not_found_does_not_exist(app):
    resp = app.get(
        "/lectures/an.15.269.PO717461/amendements",
        user="user@example.com",
        expect_errors=True,
    )
    assert resp.status_code == 404
