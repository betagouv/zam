from pathlib import Path
import transaction

import responses

from zam_repondeur.fetch.an.amendements import build_url

HERE = Path(__file__)
SAMPLE_DATA_DIR = HERE.parent / "fetch" / "sample_data"


def read_sample_data(basename):
    return (SAMPLE_DATA_DIR / basename).read_text()


def test_get_form(app, lecture_an, amendements_an):
    resp = app.get("/lectures/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert resp.forms["manual-refresh"].method == "post"
    assert (
        resp.forms["manual-refresh"].action
        == "http://localhost/lectures/an.15.269.PO717460/manual_refresh"
    )

    assert list(resp.forms["manual-refresh"].fields.keys()) == ["refresh"]

    assert resp.forms["manual-refresh"].fields["refresh"][0].attrs["type"] == "submit"


@responses.activate
def test_post_form(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession, Amendement

    responses.add(
        responses.GET,
        build_url(15, 269),
        body=read_sample_data("an_liste.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 177),
        body=read_sample_data("an_177.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 270),
        body=read_sample_data("an_270.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 723),
        body=read_sample_data("an_723.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 135),
        body=read_sample_data("an_135.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 192),
        body=read_sample_data("an_192.xml"),
        status=200,
    )

    responses.add(
        responses.GET,
        "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
        body=(Path(__file__).parent / "sample_data" / "pl0269.html").read_text(
            "utf-8", "ignore"
        ),
        status=200,
    )

    # Add a response to one of the amendements
    with transaction.manager:
        amendement = amendements_an[1]
        amendement.avis = "Favorable"
        amendement.observations = "Observations"
        amendement.reponse = "Réponse"

        # The object is no longer bound to a session here, as it was created in a
        # previous transaction, so we add it to the current session to make sure that
        # our changes will be committed with the current transaction
        DBSession.add(amendement)

    form = app.get("/lectures/").forms["manual-refresh"]
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "5 nouveaux amendements récupérés." in resp.text

    # Check that the response was preserved on the updated amendement
    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.avis == "Favorable"
    assert amendement.observations == "Observations"
    assert amendement.reponse == "Réponse"
    assert amendement.position == 2

    # Check that article content is filled.
    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.article.contenu["001"].startswith("Au titre de l'exercice 2016")
