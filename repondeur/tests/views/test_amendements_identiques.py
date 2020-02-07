import transaction


def test_amendements_not_identiques(app, lecture_an_url, amendements_an, user_david):
    resp = app.get(f"{lecture_an_url}/amendements/", user=user_david)

    assert resp.status_code == 200

    amendements = resp.parser.css("tbody tr")
    assert len(amendements) == 2

    identiques = resp.parser.css("tbody tr td.identique")
    assert len(identiques) == 0


def test_amendements_identiques(app, lecture_an_url, amendements_an, user_david):
    from zam_repondeur.models import AmendementList, DBSession

    with transaction.manager:
        DBSession.add_all(amendements_an)
        amendements_an[0].id_identique = 42
        amendements_an[1].id_identique = 42

        amdt_list = AmendementList(amendements_an)

        assert amdt_list.all_identiques(amendements_an[0]) == [amendements_an[1]]
        assert amdt_list.all_identiques(amendements_an[1]) == [amendements_an[0]]

    resp = app.get(f"{lecture_an_url}/amendements/", user=user_david)

    assert resp.status_code == 200

    amendements = resp.parser.css("tbody tr")
    assert len(amendements) == 2

    identiques = resp.parser.css("tbody tr td.identique")
    assert len(identiques) == 2

    assert "first" in identiques[0].attributes["class"]
    assert "last" not in identiques[0].attributes["class"]
    assert "first" not in identiques[1].attributes["class"]
    assert "last" in identiques[1].attributes["class"]


def test_amendements_identiques_with_abandoned(
    app, lecture_an_url, amendements_an, user_david
):
    from zam_repondeur.models import AmendementList, DBSession

    with transaction.manager:
        DBSession.add_all(amendements_an)

        amendements_an[0].id_identique = 42
        amendements_an[1].id_identique = 42
        amendements_an[1].sort = "retiré"

        assert amendements_an[1].is_abandoned

        amdt_list = AmendementList(amendements_an)
        assert amdt_list.all_identiques(amendements_an[0]) == []
        assert amdt_list.all_identiques(amendements_an[1]) == [amendements_an[0]]

    resp = app.get(f"{lecture_an_url}/amendements/", user=user_david)

    assert resp.status_code == 200

    amendements = resp.parser.css("tbody tr")
    assert len(amendements) == 2

    identiques = resp.parser.css("tbody tr td.identique")
    assert len(identiques) == 0
