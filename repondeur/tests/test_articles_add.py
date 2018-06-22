from pathlib import Path

import responses


def test_get_form(app, dummy_lecture, dummy_amendements):
    resp = app.get("/lectures/an/15/269/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert resp.form.method == "post"
    assert resp.form.action == "http://localhost/lectures/an/15/269/articles/fetch"

    assert list(resp.form.fields.keys()) == ["fetch"]

    assert resp.form.fields["fetch"][0].attrs["type"] == "submit"


@responses.activate
def test_post_form(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession, Amendement

    responses.add(
        responses.GET,
        "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
        body=(Path(__file__).parent / "sample_data" / "an0269.html").read_text(
            "utf-8", "ignore"
        ),
        status=200,
    )

    form = app.get("/lectures/an/15/269/").form

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an/15/269/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Articles récupérés" in resp.text

    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.subdiv_contenu["001"].startswith("Au titre de l'exercice 2016")
