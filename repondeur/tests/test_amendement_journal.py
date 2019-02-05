import transaction


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
        "/lectures/an.15.269.PO717460/amendements/666/amendement_journal",
        user=user_david.email,
    )
    assert first_summary_text(resp) == "David a mis l’avis à « Favorable »"


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
        "/lectures/an.15.269.PO717460/amendements/666/amendement_journal",
        user=user_david.email,
    )
    assert (
        first_summary_text(resp)
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
        "/lectures/an.15.269.PO717460/amendements/666/amendement_journal",
        user=user_david.email,
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
        "/lectures/an.15.269.PO717460/amendements/666/amendement_journal",
        user=user_david.email,
    )
    assert first_summary_text(resp) == "David a modifié la réponse"
    assert first_details_text(resp) == "De «  » à « Réponse »"


def test_amendement_journal_affectation(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models.events.amendement import AmendementTransfere

    with transaction.manager:
        AmendementTransfere.create(
            request=None,
            amendement=amendements_an[0],
            affectation="5C",
            user=user_david,
        )
        assert len(amendements_an[0].events) == 1
        assert amendements_an[0].events[0].data["old_value"] == ""
        assert amendements_an[0].events[0].data["new_value"] == "5C"

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/666/amendement_journal",
        user=user_david.email,
    )
    assert first_summary_text(resp) == "David a transféré l’amendement à « 5C »"


def test_amendement_journal_affectation_with_existing_affectation(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models.events.amendement import AmendementTransfere

    with transaction.manager:
        AmendementTransfere.create(
            request=None,
            amendement=amendements_an[0],
            affectation="5C",
            user=user_david,
        )
        AmendementTransfere.create(
            request=None,
            amendement=amendements_an[0],
            affectation="5C SD",
            user=user_david,
        )
        assert len(amendements_an[0].events) == 2
        assert amendements_an[0].events[0].data["old_value"] == "5C"
        assert amendements_an[0].events[0].data["new_value"] == "5C SD"

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/666/amendement_journal",
        user=user_david.email,
    )
    assert (
        first_summary_text(resp)
        == "David a transféré l’amendement de « 5C » à « 5C SD »"
    )
