import transaction


def first_description_text(resp):
    return resp.parser.css_first(".timeline li .what").text().strip()


def first_details_text(resp):
    return (
        resp.parser.css_first(".timeline li details")
        .text()
        .strip()
        .split("\n")[-1]
        .strip()
    )


def first_summary_text(resp):
    return resp.parser.css_first(".timeline li details summary").text()


def test_amendement_journal_avis(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models.events.amendement import AvisAmendementModifie

    with transaction.manager:
        AvisAmendementModifie.create(
            request=None,
            amendement=amendements_an[0],
            avis="Favorable",
            user=user_david,
        )
        assert len(amendements_an[0].events) == 1
        assert amendements_an[0].events[0].data["old_value"] == ""
        assert amendements_an[0].events[0].data["new_value"] == "Favorable"

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/666/journal", user=user_david.email
    )
    assert first_description_text(resp) == "David a mis l’avis à « Favorable »"


def test_amendement_journal_avis_with_existing_avis(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models.events.amendement import AvisAmendementModifie

    with transaction.manager:
        AvisAmendementModifie.create(
            request=None,
            amendement=amendements_an[0],
            avis="Favorable",
            user=user_david,
        )
        AvisAmendementModifie.create(
            request=None,
            amendement=amendements_an[0],
            avis="Défavorable",
            user=user_david,
        )
        assert len(amendements_an[0].events) == 2
        assert amendements_an[0].events[0].data["old_value"] == "Favorable"
        assert amendements_an[0].events[0].data["new_value"] == "Défavorable"

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/666/journal", user=user_david.email
    )
    assert (
        first_description_text(resp)
        == "David a modifié l’avis de « Favorable » à « Défavorable »"
    )


def test_amendement_journal_objet(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models.events.amendement import ObjetAmendementModifie

    with transaction.manager:
        ObjetAmendementModifie.create(
            request=None, amendement=amendements_an[0], objet="Objet", user=user_david
        )
        assert len(amendements_an[0].events) == 1
        assert amendements_an[0].events[0].data["old_value"] == ""
        assert amendements_an[0].events[0].data["new_value"] == "Objet"

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/666/journal", user=user_david.email
    )
    assert first_summary_text(resp) == "David a modifié l’objet"
    assert first_details_text(resp) == "De «  » à « Objet »"


def test_amendement_journal_reponse(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models.events.amendement import ReponseAmendementModifiee

    with transaction.manager:
        ReponseAmendementModifiee.create(
            request=None,
            amendement=amendements_an[0],
            reponse="Réponse",
            user=user_david,
        )
        assert len(amendements_an[0].events) == 1
        assert amendements_an[0].events[0].data["old_value"] == ""
        assert amendements_an[0].events[0].data["new_value"] == "Réponse"

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/666/journal", user=user_david.email
    )
    assert first_summary_text(resp) == "David a modifié la réponse"
    assert first_details_text(resp) == "De «  » à « Réponse »"


def test_amendement_journal_affectation(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models.events.amendement import AmendementTransfere

    with transaction.manager:
        AmendementTransfere.create(
            request=None,
            amendement=amendements_an[0],
            old_value=str(user_david),
            new_value=str(user_ronan),
            user=user_david,
        )
        assert len(amendements_an[0].events) == 1
        assert (
            amendements_an[0].events[0].data["old_value"] == "David (david@example.com)"
        )
        assert (
            amendements_an[0].events[0].data["new_value"] == "Ronan (ronan@example.com)"
        )

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/666/journal", user=user_david.email
    )
    assert (
        first_description_text(resp)
        == "David a transféré l’amendement à « Ronan (ronan@example.com) »"
    )


def test_amendement_journal_affectation_by_other(
    app, lecture_an, amendements_an, user_david, user_ronan, user_daniel
):
    from zam_repondeur.models.events.amendement import AmendementTransfere

    with transaction.manager:
        AmendementTransfere.create(
            request=None,
            amendement=amendements_an[0],
            old_value=str(user_ronan),
            new_value=str(user_daniel),
            user=user_david,
        )
        assert len(amendements_an[0].events) == 1
        assert (
            amendements_an[0].events[0].data["old_value"] == "Ronan (ronan@example.com)"
        )
        assert (
            amendements_an[0].events[0].data["new_value"]
            == "Daniel (daniel@example.com)"
        )

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/666/journal", user=user_david.email
    )
    assert first_description_text(resp) == (
        "David a transféré l’amendement de "
        "« Ronan (ronan@example.com) » à « Daniel (daniel@example.com) »"
    )


def test_amendement_journal_affectation_taken(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models.events.amendement import AmendementTransfere

    with transaction.manager:
        AmendementTransfere.create(
            request=None,
            amendement=amendements_an[0],
            old_value="",
            new_value=str(user_david),
            user=user_david,
        )
        assert len(amendements_an[0].events) == 1
        assert amendements_an[0].events[0].data["old_value"] == ""
        assert (
            amendements_an[0].events[0].data["new_value"] == "David (david@example.com)"
        )

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/666/journal", user=user_david.email
    )
    assert first_description_text(resp) == "David a mis l’amendement sur sa table"


def test_amendement_journal_affectation_taken_by_other(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models.events.amendement import AmendementTransfere

    with transaction.manager:
        AmendementTransfere.create(
            request=None,
            amendement=amendements_an[0],
            old_value="",
            new_value=str(user_david),
            user=user_ronan,
        )
        assert len(amendements_an[0].events) == 1
        assert amendements_an[0].events[0].data["old_value"] == ""
        assert (
            amendements_an[0].events[0].data["new_value"] == "David (david@example.com)"
        )

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/666/journal", user=user_david.email
    )
    assert (
        first_description_text(resp)
        == "Ronan a mis l’amendement sur la table de « David (david@example.com) »"
    )


def test_amendement_journal_affectation_released(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models.events.amendement import AmendementTransfere

    with transaction.manager:
        AmendementTransfere.create(
            request=None,
            amendement=amendements_an[0],
            old_value=str(user_david),
            new_value="",
            user=user_david,
        )
        assert len(amendements_an[0].events) == 1
        assert (
            amendements_an[0].events[0].data["old_value"] == "David (david@example.com)"
        )
        assert amendements_an[0].events[0].data["new_value"] == ""

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/666/journal", user=user_david.email
    )
    assert first_description_text(resp) == "David a remis l’amendement dans l’index"


def test_amendement_journal_affectation_released_by_other(
    app, lecture_an, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models.events.amendement import AmendementTransfere

    with transaction.manager:
        AmendementTransfere.create(
            request=None,
            amendement=amendements_an[0],
            old_value=str(user_david),
            new_value="",
            user=user_ronan,
        )
        assert len(amendements_an[0].events) == 1
        assert (
            amendements_an[0].events[0].data["old_value"] == "David (david@example.com)"
        )
        assert amendements_an[0].events[0].data["new_value"] == ""

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/666/journal", user=user_david.email
    )
    assert (
        first_description_text(resp)
        == "Ronan a remis l’amendement de « David (david@example.com) » dans l’index"
    )
