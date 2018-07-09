from pathlib import Path
import transaction

import responses


def test_get_form(app, dummy_lecture, dummy_amendements):
    resp = app.get("/lectures/an/15/269/PO717460/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert resp.forms["retrieve-textes"].method == "post"
    assert (
        resp.forms["retrieve-textes"].action
        == "http://localhost/lectures/an/15/269/PO717460/articles/fetch"
    )

    assert list(resp.forms["retrieve-textes"].fields.keys()) == ["fetch"]

    assert resp.forms["retrieve-textes"].fields["fetch"][0].attrs["type"] == "submit"


@responses.activate
def test_post_form(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession, Amendement

    responses.add(
        responses.GET,
        "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
        body=(Path(__file__).parent / "sample_data" / "pl0269.html").read_text(
            "utf-8", "ignore"
        ),
        status=200,
    )

    form = app.get("/lectures/an/15/269/PO717460/").forms["retrieve-textes"]

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an/15/269/PO717460/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Articles récupérés" in resp.text

    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.subdiv_contenu["001"].startswith("Au titre de l'exercice 2016")


@responses.activate
def test_post_form_seance(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession, Amendement

    with transaction.manager:
        dummy_lecture.num_texte = 575
        dummy_lecture.titre = "Première lecture – Séance publique"

        amendement = dummy_amendements[0]
        amendement.num_texte = 575
        amendement.subdiv_num = "2"

        # The objects are no longer bound to a session here, as they were created in a
        # previous transaction, so we add them to the current session to make sure that
        # our changes will be committed with the current transaction
        DBSession.add(dummy_lecture)
        DBSession.add(amendement)

    responses.add(
        responses.GET,
        "http://www.assemblee-nationale.fr/15/projets/pl0575.asp",
        status=404,
    )
    responses.add(
        responses.GET,
        "http://www.assemblee-nationale.fr/15/ta-commission/r0575-a0.asp",
        body=(Path(__file__).parent / "sample_data" / "r0575-a0.html").read_text(
            "utf-8", "ignore"
        ),
        status=200,
    )

    form = app.get("/lectures/an/15/575/PO717460/").forms["retrieve-textes"]

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an/15/575/PO717460/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Articles récupérés" in resp.text

    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.subdiv_contenu["001"].startswith("Le code des relations entre")


@responses.activate
def test_post_form_senat(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession, Amendement

    with transaction.manager:
        dummy_lecture.chambre = "senat"
        dummy_lecture.session = "2017-2018"
        dummy_lecture.num_texte = 63
        dummy_lecture.organe = "PO78718"

        amendement = dummy_amendements[0]
        amendement.chambre = "senat"
        amendement.session = "2017-2018"
        amendement.num_texte = 63
        amendement.organe = "PO78718"
        amendement.subdiv_num = "1"

        # The objects are no longer bound to a session here, as they were created in a
        # previous transaction, so we add them to the current session to make sure that
        # our changes will be committed with the current transaction
        DBSession.add(dummy_lecture)
        DBSession.add(amendement)

    responses.add(
        responses.GET,
        "https://www.senat.fr/leg/pjl17-063.html",
        body=(Path(__file__).parent / "sample_data" / "pjl17-063.html").read_text(
            "utf-8", "ignore"
        ),
        status=200,
    )

    form = app.get("/lectures/senat/2017-2018/63/PO78718/").forms["retrieve-textes"]

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/senat/2017-2018/63/PO78718/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Articles récupérés" in resp.text

    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.subdiv_contenu["001"].startswith("Au titre de l'exercice 2016")


@responses.activate
def test_post_form_senat_with_mult(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession, Amendement

    with transaction.manager:
        dummy_lecture.chambre = "senat"
        dummy_lecture.session = "2017-2018"
        dummy_lecture.num_texte = 63
        dummy_lecture.organe = "PO78718"

        amendement = dummy_amendements[0]
        amendement.chambre = "senat"
        amendement.session = "2017-2018"
        amendement.num_texte = 63
        amendement.organe = "PO78718"
        amendement.subdiv_num = "4"
        amendement.subdiv_mult = "bis"

        # The objects are no longer bound to a session here, as they were created in a
        # previous transaction, so we add them to the current session to make sure that
        # our changes will be committed with the current transaction
        DBSession.add(dummy_lecture)
        DBSession.add(amendement)

    responses.add(
        responses.GET,
        "https://www.senat.fr/leg/pjl17-063.html",
        body=(Path(__file__).parent / "sample_data" / "pjl17-063.html").read_text(
            "utf-8", "ignore"
        ),
        status=200,
    )

    form = app.get("/lectures/senat/2017-2018/63/PO78718/").forms["retrieve-textes"]

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/senat/2017-2018/63/PO78718/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Articles récupérés" in resp.text

    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.subdiv_contenu["001"].startswith("Ne donnent pas lieu à")
