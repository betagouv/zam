import transaction
from pyramid.testing import DummyRequest


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


def test_amendement_journal_avis(app, lecture_an_url, amendements_an, user_david):
    from zam_repondeur.models.events.amendement import AvisAmendementModifie

    with transaction.manager:
        AvisAmendementModifie.create(
            amendement=amendements_an[0],
            avis="Favorable",
            request=DummyRequest(remote_addr="127.0.0.1", user=user_david),
        )
        assert len(amendements_an[0].events) == 1
        assert amendements_an[0].events[0].data["old_value"] == ""
        assert amendements_an[0].events[0].data["new_value"] == "Favorable"

    resp = app.get(f"{lecture_an_url}/amendements/666/journal", user=user_david)
    assert first_description_text(resp) == "David a mis l’avis à « Favorable »."


def test_amendement_journal_avis_with_existing_avis(
    app, lecture_an_url, amendements_an, user_david
):
    from zam_repondeur.models.events.amendement import AvisAmendementModifie

    with transaction.manager:
        AvisAmendementModifie.create(
            amendement=amendements_an[0],
            avis="Favorable",
            request=DummyRequest(remote_addr="127.0.0.1", user=user_david),
        )
        AvisAmendementModifie.create(
            amendement=amendements_an[0],
            avis="Défavorable",
            request=DummyRequest(remote_addr="127.0.0.1", user=user_david),
        )
        assert len(amendements_an[0].events) == 2
        assert amendements_an[0].events[0].data["old_value"] == "Favorable"
        assert amendements_an[0].events[0].data["new_value"] == "Défavorable"

    resp = app.get(f"{lecture_an_url}/amendements/666/journal", user=user_david)
    assert (
        first_description_text(resp)
        == "David a modifié l’avis de « Favorable » à « Défavorable »."
    )


def test_amendement_journal_objet(app, lecture_an_url, amendements_an, user_david):
    from zam_repondeur.models.events.amendement import ObjetAmendementModifie

    with transaction.manager:
        ObjetAmendementModifie.create(
            amendement=amendements_an[0],
            objet="Objet",
            request=DummyRequest(remote_addr="127.0.0.1", user=user_david),
        )
        assert len(amendements_an[0].events) == 1
        assert amendements_an[0].events[0].data["old_value"] == ""
        assert amendements_an[0].events[0].data["new_value"] == "Objet"

    resp = app.get(f"{lecture_an_url}/amendements/666/journal", user=user_david)
    assert first_summary_text(resp) == "David a ajouté l’objet."
    assert first_details_text(resp) == "Objet"


def test_amendement_journal_reponse(app, lecture_an_url, amendements_an, user_david):
    from zam_repondeur.models.events.amendement import ReponseAmendementModifiee

    with transaction.manager:
        ReponseAmendementModifiee.create(
            amendement=amendements_an[0],
            reponse="Réponse",
            request=DummyRequest(remote_addr="127.0.0.1", user=user_david),
        )
        assert len(amendements_an[0].events) == 1
        assert amendements_an[0].events[0].data["old_value"] == ""
        assert amendements_an[0].events[0].data["new_value"] == "Réponse"

    resp = app.get(f"{lecture_an_url}/amendements/666/journal", user=user_david)
    assert first_summary_text(resp) == "David a ajouté la réponse."
    assert first_details_text(resp) == "Réponse"


def test_amendement_journal_comments(app, lecture_an_url, amendements_an, user_david):
    from zam_repondeur.models.events.amendement import CommentsAmendementModifie

    with transaction.manager:
        CommentsAmendementModifie.create(
            amendement=amendements_an[0],
            comments="Un commentaire",
            request=DummyRequest(remote_addr="127.0.0.1", user=user_david),
        )
        assert len(amendements_an[0].events) == 1
        assert amendements_an[0].events[0].data["old_value"] == ""
        assert amendements_an[0].events[0].data["new_value"] == "Un commentaire"

    resp = app.get(f"{lecture_an_url}/amendements/666/journal", user=user_david)
    assert first_summary_text(resp) == "David a ajouté des commentaires."
    assert first_details_text(resp) == "Un commentaire"


def test_amendement_journal_affectation(
    app, lecture_an_url, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models.events.amendement import AmendementTransfere

    with transaction.manager:
        AmendementTransfere.create(
            amendement=amendements_an[0],
            old_value=str(user_david),
            new_value=str(user_ronan),
            request=DummyRequest(remote_addr="127.0.0.1", user=user_david),
        )
        assert len(amendements_an[0].events) == 1
        assert (
            amendements_an[0].events[0].data["old_value"]
            == "David (david@exemple.gouv.fr)"
        )
        assert (
            amendements_an[0].events[0].data["new_value"]
            == "Ronan (ronan@exemple.gouv.fr)"
        )

    resp = app.get(f"{lecture_an_url}/amendements/666/journal", user=user_david)
    assert (
        first_description_text(resp)
        == "David a transféré l’amendement à « Ronan (ronan@exemple.gouv.fr) »."
    )


def test_amendement_journal_affectation_by_other(
    app, lecture_an_url, amendements_an, user_david, user_ronan, user_daniel
):
    from zam_repondeur.models.events.amendement import AmendementTransfere

    with transaction.manager:
        AmendementTransfere.create(
            amendement=amendements_an[0],
            old_value=str(user_ronan),
            new_value=str(user_daniel),
            request=DummyRequest(remote_addr="127.0.0.1", user=user_david),
        )
        assert len(amendements_an[0].events) == 1
        assert (
            amendements_an[0].events[0].data["old_value"]
            == "Ronan (ronan@exemple.gouv.fr)"
        )
        assert (
            amendements_an[0].events[0].data["new_value"]
            == "Daniel (daniel@exemple.gouv.fr)"
        )

    resp = app.get(f"{lecture_an_url}/amendements/666/journal", user=user_david)
    assert first_description_text(resp) == (
        "David a transféré l’amendement de "
        "« Ronan (ronan@exemple.gouv.fr) » à « Daniel (daniel@exemple.gouv.fr) »."
    )


def test_amendement_journal_affectation_taken(
    app, lecture_an_url, amendements_an, user_david
):
    from zam_repondeur.models.events.amendement import AmendementTransfere

    with transaction.manager:
        AmendementTransfere.create(
            amendement=amendements_an[0],
            old_value="",
            new_value=str(user_david),
            request=DummyRequest(remote_addr="127.0.0.1", user=user_david),
        )
        assert len(amendements_an[0].events) == 1
        assert amendements_an[0].events[0].data["old_value"] == ""
        assert (
            amendements_an[0].events[0].data["new_value"]
            == "David (david@exemple.gouv.fr)"
        )

    resp = app.get(f"{lecture_an_url}/amendements/666/journal", user=user_david)
    assert first_description_text(resp) == "David a mis l’amendement sur sa table."


def test_amendement_journal_affectation_taken_by_other(
    app, lecture_an_url, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models.events.amendement import AmendementTransfere

    with transaction.manager:
        AmendementTransfere.create(
            amendement=amendements_an[0],
            old_value="",
            new_value=str(user_david),
            request=DummyRequest(remote_addr="127.0.0.1", user=user_ronan),
        )
        assert len(amendements_an[0].events) == 1
        assert amendements_an[0].events[0].data["old_value"] == ""
        assert (
            amendements_an[0].events[0].data["new_value"]
            == "David (david@exemple.gouv.fr)"
        )

    resp = app.get(f"{lecture_an_url}/amendements/666/journal", user=user_david)
    assert (
        first_description_text(resp)
        == "Ronan a transféré l’amendement à « David (david@exemple.gouv.fr) »."
    )


def test_amendement_journal_affectation_released(
    app, lecture_an_url, amendements_an, user_david
):
    from zam_repondeur.models.events.amendement import AmendementTransfere

    with transaction.manager:
        AmendementTransfere.create(
            amendement=amendements_an[0],
            old_value=str(user_david),
            new_value="",
            request=DummyRequest(remote_addr="127.0.0.1", user=user_david),
        )
        assert len(amendements_an[0].events) == 1
        assert (
            amendements_an[0].events[0].data["old_value"]
            == "David (david@exemple.gouv.fr)"
        )
        assert amendements_an[0].events[0].data["new_value"] == ""

    resp = app.get(f"{lecture_an_url}/amendements/666/journal", user=user_david)
    assert first_description_text(resp) == "David a remis l’amendement dans l’index."


def test_amendement_journal_affectation_released_by_other(
    app, lecture_an_url, amendements_an, user_david, user_ronan
):
    from zam_repondeur.models.events.amendement import AmendementTransfere

    with transaction.manager:
        AmendementTransfere.create(
            amendement=amendements_an[0],
            old_value=str(user_david),
            new_value="",
            request=DummyRequest(remote_addr="127.0.0.1", user=user_ronan),
        )
        assert len(amendements_an[0].events) == 1
        assert (
            amendements_an[0].events[0].data["old_value"]
            == "David (david@exemple.gouv.fr)"
        )
        assert amendements_an[0].events[0].data["new_value"] == ""

    resp = app.get(f"{lecture_an_url}/amendements/666/journal", user=user_david)
    assert first_description_text(resp) == (
        "Ronan a remis l’amendement de "
        "« David (david@exemple.gouv.fr) » dans l’index."
    )
