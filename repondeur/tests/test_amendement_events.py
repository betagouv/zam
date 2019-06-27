import transaction


def test_post_amendement_init_form_events(
    app, lecture_an, amendements_an, user_david, user_david_table_an
):
    from zam_repondeur.models import Amendement, DBSession
    from zam_repondeur.models.events.amendement import (
        AvisAmendementModifie,
        ObjetAmendementModifie,
        ReponseAmendementModifiee,
        CommentsAmendementModifie,
    )

    amendement = amendements_an[1]

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendement)

    resp = app.get(
        f"/lectures/an.15.269.PO717460/amendements/{amendement.num}/amendement_edit",
        user=user_david,
    )
    form = resp.forms["edit-amendement"]
    form["avis"] = "Favorable"
    form["objet"] = "Un objet très pertinent"
    form["reponse"] = "Une réponse <strong>très</strong> appropriée"
    form["comments"] = "Avec des <table><tr><td>commentaires</td></tr></table>"
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location.endswith(
        f"/an.15.269.PO717460/tables/david@exemple.gouv.fr/#amdt-{amendement.num}"
    )

    amendement = (
        DBSession.query(Amendement).filter(Amendement.num == amendement.num).one()
    )

    # Events created.
    assert len(amendement.events) == 4
    assert isinstance(amendement.events[0], CommentsAmendementModifie)
    assert amendement.events[0].created_at is not None
    assert amendement.events[0].user.email == "david@exemple.gouv.fr"
    assert amendement.events[0].data["old_value"] == ""
    assert (
        amendement.events[0].data["new_value"]
        == "Avec des <table><tbody><tr><td>commentaires</td></tr></tbody></table>"
    )
    assert isinstance(amendement.events[1], ReponseAmendementModifiee)
    assert amendement.events[1].created_at is not None
    assert amendement.events[1].user.email == "david@exemple.gouv.fr"
    assert amendement.events[1].data["old_value"] == ""
    assert (
        amendement.events[1].data["new_value"]
        == "Une réponse <strong>très</strong> appropriée"
    )
    assert isinstance(amendement.events[2], ObjetAmendementModifie)
    assert amendement.events[2].created_at is not None
    assert amendement.events[2].user.email == "david@exemple.gouv.fr"
    assert amendement.events[2].data["old_value"] == ""
    assert amendement.events[2].data["new_value"] == "Un objet très pertinent"
    assert isinstance(amendement.events[3], AvisAmendementModifie)
    assert amendement.events[3].created_at is not None
    assert amendement.events[3].user.email == "david@exemple.gouv.fr"
    assert amendement.events[3].data["old_value"] == ""
    assert amendement.events[3].data["new_value"] == "Favorable"

    # Events rendering.
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> a ajouté des commentaires."
    )
    assert amendement.events[0].render_details() == (
        "<ins>Avec des </ins>"
        "<table><tbody><tr><td><ins>commentaires</ins></td></tr></tbody></table> "
        "<del></del>"
    )
    assert amendement.events[1].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> a ajouté la réponse."
    )
    assert (
        amendement.events[1].render_details()
        == "<ins>Une réponse <strong>très</strong> appropriée</ins> <del></del>"
    )
    assert amendement.events[2].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> a ajouté l’objet."
    )
    assert (
        amendement.events[2].render_details()
        == "<ins>Un objet très pertinent</ins> <del></del>"
    )
    assert amendement.events[3].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> a mis l’avis à « Favorable »."
    )
    assert amendement.events[3].render_details() == ""


def test_post_amendement_edit_form_events(
    app, lecture_an, amendements_an, user_david, user_david_table_an
):
    from zam_repondeur.models import Amendement, DBSession
    from zam_repondeur.models.events.amendement import (
        AvisAmendementModifie,
        ObjetAmendementModifie,
        ReponseAmendementModifiee,
        CommentsAmendementModifie,
    )

    amendement = amendements_an[1]

    with transaction.manager:
        DBSession.add(user_david_table_an)
        amendement.user_content.avis = "Défavorable"
        amendement.user_content.objet = "Un objet assez passable"
        amendement.user_content.reponse = "Des réponses <strong>très</strong> bonnes"
        amendement.user_content.comments = "Avec"
        user_david_table_an.amendements.append(amendement)

    resp = app.get(
        f"/lectures/an.15.269.PO717460/amendements/{amendement.num}/amendement_edit",
        user=user_david,
    )
    form = resp.forms["edit-amendement"]
    form["avis"] = "Favorable"
    form["objet"] = "Un objet très pertinent"
    form["reponse"] = "Une réponse <strong>très</strong> appropriée"
    form["comments"] = "Avec des <table><tr><td>commentaires</td></tr></table>"
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location.endswith(
        f"/an.15.269.PO717460/tables/david@exemple.gouv.fr/#amdt-{amendement.num}"
    )

    amendement = (
        DBSession.query(Amendement).filter(Amendement.num == amendement.num).one()
    )

    # Events created.
    assert len(amendement.events) == 4
    assert isinstance(amendement.events[0], CommentsAmendementModifie)
    assert amendement.events[0].created_at is not None
    assert amendement.events[0].user.email == "david@exemple.gouv.fr"
    assert amendement.events[0].data["old_value"] == "Avec"
    assert (
        amendement.events[0].data["new_value"]
        == "Avec des <table><tbody><tr><td>commentaires</td></tr></tbody></table>"
    )
    assert isinstance(amendement.events[1], ReponseAmendementModifiee)
    assert amendement.events[1].created_at is not None
    assert amendement.events[1].user.email == "david@exemple.gouv.fr"
    assert (
        amendement.events[1].data["old_value"]
        == "Des réponses <strong>très</strong> bonnes"
    )
    assert (
        amendement.events[1].data["new_value"]
        == "Une réponse <strong>très</strong> appropriée"
    )
    assert isinstance(amendement.events[2], ObjetAmendementModifie)
    assert amendement.events[2].created_at is not None
    assert amendement.events[2].user.email == "david@exemple.gouv.fr"
    assert amendement.events[2].data["old_value"] == "Un objet assez passable"
    assert amendement.events[2].data["new_value"] == "Un objet très pertinent"
    assert isinstance(amendement.events[3], AvisAmendementModifie)
    assert amendement.events[3].created_at is not None
    assert amendement.events[3].user.email == "david@exemple.gouv.fr"
    assert amendement.events[3].data["old_value"] == "Défavorable"
    assert amendement.events[3].data["new_value"] == "Favorable"

    # Events rendering.
    assert amendement.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> a modifié les commentaires."
    )
    assert amendement.events[0].render_details() == (
        "Avec <ins>des </ins>"
        "<table><tbody><tr><td><ins>commentaires</ins></td></tr></tbody></table>"
    )
    assert amendement.events[1].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> a modifié la réponse."
    )
    assert amendement.events[1].render_details() == (
        "<ins>Une réponse <strong>très</strong> appropriée</ins> "
        "<del>Des réponses <strong>très</strong> bonnes</del>"
    )
    assert amendement.events[2].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> a modifié l’objet."
    )
    assert (
        amendement.events[2].render_details()
        == "Un objet <ins>très pertinent</ins> <del>assez passable</del>"
    )
    assert amendement.events[3].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> a modifié l’avis de "
        "« Défavorable » à « Favorable »."
    )
    assert amendement.events[3].render_details() == ""


def test_post_amendement_edit_form_events_empty(
    app, lecture_an, amendements_an, user_david, user_david_table_an
):
    from zam_repondeur.models import Amendement, DBSession

    amendement = amendements_an[1]

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendement)

    resp = app.get(
        f"/lectures/an.15.269.PO717460/amendements/{amendement.num}/amendement_edit",
        user=user_david,
    )
    form = resp.forms["edit-amendement"]
    form["avis"] = ""
    form["objet"] = ""
    form["reponse"] = ""
    form["comments"] = ""
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location.endswith(
        f"/an.15.269.PO717460/tables/david@exemple.gouv.fr/#amdt-{amendement.num}"
    )

    amendement = (
        DBSession.query(Amendement).filter(Amendement.num == amendement.num).one()
    )

    # Events not created.
    assert len(amendement.events) == 0
