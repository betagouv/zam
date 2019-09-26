import transaction


def test_get_amendements(app, lecture_an_url, amendements_an, user_david):
    resp = app.get(f"{lecture_an_url}/amendements/", user=user_david)

    assert resp.status_code == 200
    assert "Dossier de banc" not in resp.text


def test_no_amendements(app, lecture_an_url, user_david):
    resp = app.get(f"{lecture_an_url}/amendements/", user=user_david)

    assert resp.status_code == 200
    assert "Dossier de banc" not in resp.text
    assert "Les amendements ne sont pas encore disponibles." in resp.text


def test_get_amendements_with_avis(app, lecture_an_url, amendements_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendement = amendements_an[0]
        amendement.user_content.avis = "Favorable"
        DBSession.add(amendement)

    resp = app.get(f"{lecture_an_url}/amendements/", user=user_david)

    assert resp.status_code == 200
    assert "Dossier de banc" in resp.text


def test_get_amendements_with_gouvernemental(
    app, lecture_an_url, amendements_an, user_david
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendement = amendements_an[0]
        amendement.auteur = "LE GOUVERNEMENT"
        DBSession.add(amendement)

    resp = app.get(f"{lecture_an_url}/amendements/", user=user_david)

    assert resp.status_code == 200
    assert "Dossier de banc" in resp.text


def test_get_amendements_order_default(app, lecture_an_url, amendements_an, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.user_content.avis = "Favorable"
        DBSession.add_all(amendements_an)

    resp = app.get(f"{lecture_an_url}/amendements/", user=user_david)

    assert resp.status_code == 200
    assert "Dossier de banc" in resp.text
    assert [node.text().strip() for node in resp.parser.css("tr td:nth-child(3)")] == [
        "666",
        "999",
    ]
    headers_rows_length = 3
    assert [" ".join(node.text().strip().split()) for node in resp.parser.css("tr")][
        headers_rows_length:
    ] == ["Art. 1 666 Voir", "Art. 1 999 Voir"]


def test_get_amendements_order_fallback_article(
    app, lecture_an_url, amendements_an, user_david, article7bis_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        for amendement in amendements_an:
            amendement.position = None
        amendements_an[0].article = article7bis_an
        DBSession.add_all(amendements_an)

    resp = app.get(f"{lecture_an_url}/amendements/", user=user_david)

    assert resp.status_code == 200
    assert [node.text().strip() for node in resp.parser.css("tr td:nth-child(3)")] == [
        "999",
        "666",
    ]


def test_get_amendements_order_abandoned_last(
    app, lecture_an_url, amendements_an, user_david
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendements_an[0].position = None
        amendements_an[0].sort = "Irrecevable"
        for amendement in amendements_an:
            amendement.user_content.avis = "Favorable"
        DBSession.add_all(amendements_an)

    resp = app.get(f"{lecture_an_url}/amendements/", user=user_david)

    assert resp.status_code == 200
    assert "Dossier de banc" in resp.text
    headers_rows_length = 3
    assert [" ".join(node.text().strip().split()) for node in resp.parser.css("tr")][
        headers_rows_length:
    ] == [
        "Art. 1 999 Voir",
        (
            "Les amendements en-deçà de cette ligne ne sont pas (encore) présents "
            "dans le dérouleur."
        ),
        "Art. 1 666 Irr. Voir",
    ]


def test_get_amendements_order_with_missing_position(
    app, lecture_an_url, amendements_an, user_david
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendements_an[0].position = None
        for amendement in amendements_an:
            amendement.user_content.avis = "Favorable"
        DBSession.add_all(amendements_an)

    resp = app.get(f"{lecture_an_url}/amendements/", user=user_david)

    assert resp.status_code == 200
    assert "Dossier de banc" in resp.text
    headers_rows_length = 3
    assert [" ".join(node.text().strip().split()) for node in resp.parser.css("tr")][
        headers_rows_length:
    ] == [
        "Art. 1 999 Voir",
        (
            "Les amendements en-deçà de cette ligne ne sont pas (encore) présents "
            "dans le dérouleur."
        ),
        "Art. 1 666 Voir",
    ]


def test_get_amendements_not_found_bad_format(app, user_david):
    resp = app.get(
        "/dossiers/loi-finances-2018/lectures/senat.2017-2018.1/amendements/",
        user=user_david,
        expect_errors=True,
    )
    assert resp.status_code == 404


def test_get_amendements_not_found_does_not_exist(app, user_david):
    resp = app.get(
        "/dossiers/loi-finances-2018/lectures/an.15.269.PO717461/amendements/",
        user=user_david,
        expect_errors=True,
    )
    assert resp.status_code == 404


def test_get_amendements_columns_default(
    app, lecture_an_url, amendements_an, user_david
):
    resp = app.get(f"{lecture_an_url}/amendements/", user=user_david)

    assert resp.status_code == 200
    assert [
        node.text().strip().split()
        for node in resp.parser.css("thead tr.filters th")
        if node.text().strip().split()
    ] == [["Article"], ["Nº", "Gouv."], ["Table/boîte", "Vide"], ["Avis"], ["Réponse"]]


def test_get_amendements_columns_missions_for_plf2(
    app, amendements_plf2018_an_premiere_lecture_seance_publique_2, user_david
):
    resp = app.get(
        "/dossiers/loi-finances-2018/lectures/an.15.235-2.PO717460/amendements/",
        user=user_david,
    )

    assert resp.status_code == 200
    assert [
        node.text().strip().split()
        for node in resp.parser.css("thead tr.filters th")
        if node.text().strip().split()
    ] == [
        ["Article"],
        ["Mission"],
        ["Nº", "Gouv."],
        ["Table/boîte", "Vide"],
        ["Avis"],
        ["Réponse"],
    ]


def test_get_amendements_missions_title_for_plf2(
    app, amendements_plf2018_an_premiere_lecture_seance_publique_2, user_david
):
    resp = app.get(
        "/dossiers/loi-finances-2018/lectures/an.15.235-2.PO717460/amendements/",
        user=user_david,
    )

    assert resp.status_code == 200
    assert [node.text().strip() for node in resp.parser.css("tr td:nth-child(3)")] == [
        "Action transfo.",
        "Action transfo.",
    ]
