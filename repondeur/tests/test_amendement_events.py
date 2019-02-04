def test_post_amendement_edit_form_events(app, lecture_an, amendements_an):
    from zam_repondeur.models import Amendement, DBSession
    from zam_repondeur.models.events.amendement import (
        AvisAmendementModifie,
        ObjetAmendementModifie,
        ReponseAmendementModifiee,
    )

    resp = app.get(
        "/lectures/an.15.269.PO717460/amendements/999/amendement_edit",
        user="user@example.com",
    )
    form = resp.forms["edit-amendement"]
    form["avis"] = "Favorable"
    form["objet"] = "Un objet très pertinent"
    form["reponse"] = "Une réponse <strong>très</strong> appropriée"
    form["comments"] = "Avec des <table><tr><td>commentaires</td></tr></table>"
    resp = form.submit()

    assert resp.status_code == 302
    assert (
        resp.location
        == "https://zam.test/lectures/an.15.269.PO717460/spaces/user@example.com/#amdt-999"  # noqa
    )

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()

    # Events created.
    assert len(amendement.events) == 3
    assert isinstance(amendement.events[0], ReponseAmendementModifiee)
    assert amendement.events[0].created_at is not None
    assert amendement.events[0].user.email == "user@example.com"
    assert amendement.events[0].data["old_value"] == ""
    assert (
        amendement.events[0].data["new_value"]
        == "Une réponse <strong>très</strong> appropriée"
    )
    assert isinstance(amendement.events[1], ObjetAmendementModifie)
    assert amendement.events[1].created_at is not None
    assert amendement.events[1].user.email == "user@example.com"
    assert amendement.events[1].data["old_value"] == ""
    assert amendement.events[1].data["new_value"] == "Un objet très pertinent"
    assert isinstance(amendement.events[2], AvisAmendementModifie)
    assert amendement.events[2].created_at is not None
    assert amendement.events[2].user.email == "user@example.com"
    assert amendement.events[2].data["old_value"] == ""
    assert amendement.events[2].data["new_value"] == "Favorable"

    # Events rendering.
    assert amendement.events[0].render_summary() == (
        "<abbr title='user@example.com'>user@example.com</abbr> a modifié la réponse"
    )
    assert (
        amendement.events[0].render_details()
        == "De <del>«  »</del> à <ins>« Une réponse très appropriée »</ins>"
    )
    assert amendement.events[1].render_summary() == (
        "<abbr title='user@example.com'>user@example.com</abbr> a modifié l’objet"
    )
    assert (
        amendement.events[1].render_details()
        == "De <del>«  »</del> à <ins>« Un objet très pertinent »</ins>"
    )
    assert amendement.events[2].render_summary() == (
        "<abbr title='user@example.com'>user@example.com</abbr> a mis l’avis "
        "à « Favorable »"
    )
    assert amendement.events[2].render_details() == ""
