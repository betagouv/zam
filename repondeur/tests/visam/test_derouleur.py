import transaction


def test_derouleur_content(
    app,
    seance_ccfp,
    lecture_seance_ccfp,
    user_ccfp,
    amendement_222_lecture_seance_ccfp,
    amendement_444_lecture_seance_ccfp,
):
    from zam_repondeur.models import DBSession

    lecture = lecture_seance_ccfp
    dossier = lecture.dossier

    with transaction.manager:
        amendement_222_lecture_seance_ccfp.expose = "Exposé 222"
        amendement_222_lecture_seance_ccfp.corps = "Corps 222"
        amendement_444_lecture_seance_ccfp.expose = "Exposé 444"
        amendement_444_lecture_seance_ccfp.corps = "Corps 444"
        DBSession.add_all(
            [amendement_222_lecture_seance_ccfp, amendement_444_lecture_seance_ccfp]
        )

    resp = app.get(
        f"/seances/{seance_ccfp.slug}/textes/{dossier.slug}/derouleur/", user=user_ccfp,
    )
    assert resp.status_code == 200
    article_title = resp.parser.css_first("header .titles h2")
    assert article_title.text().strip() == "Article 1"
    amendements_titles = resp.parser.css(".reponse h2")
    assert [title.text().strip() for title in amendements_titles] == [
        "Amendement v222",
        "Amendement v444",
    ]
    amendements_contents = resp.parser.css(".amendement-detail")
    assert (
        " ".join(
            [
                line.strip()
                for line in amendements_contents[0].text().strip().split("\n")
            ]
        )
        == "Exposé Exposé 222 Corps de l’amendement Corps 222"
    )
    assert (
        " ".join(
            [
                line.strip()
                for line in amendements_contents[1].text().strip().split("\n")
            ]
        )
        == "Exposé Exposé 444 Corps de l’amendement Corps 444"
    )
