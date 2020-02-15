import transaction


def test_search_amendement(app, lecture_an_url, amendements_an, user_david):
    resp = app.get(
        f"{lecture_an_url}/search_amendement",
        params={"num": amendements_an[0].num},
        user=user_david,
    )

    assert resp.status_code == 200
    assert resp.content_type == "application/json"
    assert resp.json == {
        "index": (
            "https://zam.test"
            "/dossiers/plfss-2018/lectures/an.15.269.PO717460/amendements/"
            "?article=article.1..#amdt-666"
        )
    }


def test_search_amendement_with_reponse(
    app, lecture_an_url, amendements_an, user_david
):
    from zam_repondeur.models import DBSession

    amendement = amendements_an[0]
    with transaction.manager:
        DBSession.add_all(amendements_an)
        amendement.user_content.avis = "Favorable"
        amendement.user_content.reponse = "<p>Bla bla bla</p>"

    resp = app.get(
        f"{lecture_an_url}/search_amendement",
        params={"num": amendements_an[0].num},
        user=user_david,
    )

    assert resp.status_code == 200
    assert resp.content_type == "application/json"
    assert resp.json == {
        "index": (
            "https://zam.test"
            "/dossiers/plfss-2018/lectures/an.15.269.PO717460/amendements/"
            "?article=article.1..#amdt-666"
        ),
        "visionneuse": (
            "https://zam.test"
            "/dossiers/plfss-2018/lectures/an.15.269.PO717460/articles/article.1../"
            "reponses#amdt-666"
        ),
    }
