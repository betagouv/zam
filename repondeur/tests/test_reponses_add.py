from pathlib import Path

from webtest import Upload
from webtest.forms import File


def test_get_form(app, dummy_lecture):
    resp = app.get("/lectures/an/15/269/amendements/list")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    assert resp.form.method == "post"
    assert resp.form.action == ""

    assert list(resp.form.fields.keys()) == ["reponses", "upload"]

    assert isinstance(resp.form.fields["reponses"][0], File)
    assert resp.form.fields["upload"][0].attrs["type"] == "submit"


def test_post_form_reponse(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession, Amendement

    form = app.get("/lectures/an/15/269/amendements/list").form
    path = Path(__file__).parent / "sample_data" / "reponses.csv"
    form["reponses"] = Upload("file.csv", path.read_bytes())

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an/15/269/amendements/list"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "2 réponses chargées" in resp.text

    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.avis == "Défavorable"
    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
    assert amendement.observations.startswith("Lorem")
