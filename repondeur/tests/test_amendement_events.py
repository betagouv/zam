import transaction


def test_post_amendement_edit_form_events(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import Amendement, DBSession
    from zam_repondeur.models.events.amendement import (
        AvisAmendementModifie,
        ObjetAmendementModifie,
        ReponseAmendementModifiee,
    )

    amendement = amendements_an[1]

    with transaction.manager:
        DBSession.add(amendement)
        table = user_david.table_for(lecture_an)
        table.amendements.append(amendement)

    resp = app.get(
        f"/lectures/an.15.269.PO717460/amendements/{amendement.num}/amendement_edit",
        user=user_david.email,
    )
    form = resp.forms["edit-amendement"]
    form["avis"] = "Favorable"
    form["objet"] = "Un objet très pertinent"
    form["reponse"] = "Une réponse <strong>très</strong> appropriée"
    form["comments"] = "Avec des <table><tr><td>commentaires</td></tr></table>"
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location.endswith(
        f"/an.15.269.PO717460/tables/david@example.com/#amdt-{amendement.num}"
    )

    amendement = (
        DBSession.query(Amendement).filter(Amendement.num == amendement.num).one()
    )

    # Events created.
    assert len(amendement.events) == 3
    assert isinstance(amendement.events[0], ReponseAmendementModifiee)
    assert amendement.events[0].created_at is not None
    assert amendement.events[0].user.email == "david@example.com"
    assert amendement.events[0].data["old_value"] == ""
    assert (
        amendement.events[0].data["new_value"]
        == "Une réponse <strong>très</strong> appropriée"
    )
    assert isinstance(amendement.events[1], ObjetAmendementModifie)
    assert amendement.events[1].created_at is not None
    assert amendement.events[1].user.email == "david@example.com"
    assert amendement.events[1].data["old_value"] == ""
    assert amendement.events[1].data["new_value"] == "Un objet très pertinent"
    assert isinstance(amendement.events[2], AvisAmendementModifie)
    assert amendement.events[2].created_at is not None
    assert amendement.events[2].user.email == "david@example.com"
    assert amendement.events[2].data["old_value"] == ""
    assert amendement.events[2].data["new_value"] == "Favorable"

    # Events rendering.
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> a modifié la réponse"
    )
    assert (
        amendement.events[0].render_details()
        == "De <del>«  »</del> à <ins>« Une réponse très appropriée »</ins>"
    )
    assert amendement.events[1].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> a modifié l’objet"
    )
    assert (
        amendement.events[1].render_details()
        == "De <del>«  »</del> à <ins>« Un objet très pertinent »</ins>"
    )
    assert amendement.events[2].render_summary() == (
        "<abbr title='david@example.com'>David</abbr> a mis l’avis " "à « Favorable »"
    )
    assert amendement.events[2].render_details() == ""


def test_post_amendement_edit_form_events_empty(
    app, lecture_an, amendements_an, user_david
):
    from zam_repondeur.models import Amendement, DBSession

    amendement = amendements_an[1]

    with transaction.manager:
        DBSession.add(amendement)
        table = user_david.table_for(lecture_an)
        table.amendements.append(amendement)

    resp = app.get(
        f"/lectures/an.15.269.PO717460/amendements/{amendement.num}/amendement_edit",
        user=user_david.email,
    )
    form = resp.forms["edit-amendement"]
    form["avis"] = ""
    form["objet"] = ""
    form["reponse"] = ""
    form["comments"] = ""
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location.endswith(
        f"/an.15.269.PO717460/tables/david@example.com/#amdt-{amendement.num}"
    )

    amendement = (
        DBSession.query(Amendement).filter(Amendement.num == amendement.num).one()
    )

    # Events not created.
    assert len(amendement.events) == 0
