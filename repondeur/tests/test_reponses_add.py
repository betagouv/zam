import transaction
from pathlib import Path

from webtest import Upload
from webtest.forms import File


def test_get_form(app, dummy_lecture):
    resp = app.get("/lectures/an/15/269/PO717460/amendements/list")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    assert resp.form.method == "post"
    assert resp.form.action == ""

    assert list(resp.form.fields.keys()) == ["reponses", "upload"]

    assert isinstance(resp.form.fields["reponses"][0], File)
    assert resp.form.fields["upload"][0].attrs["type"] == "submit"


def test_post_form(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession, Amendement

    form = app.get("/lectures/an/15/269/PO717460/amendements/list").form
    path = Path(__file__).parent / "sample_data" / "reponses.csv"
    form["reponses"] = Upload("file.csv", path.read_bytes())

    resp = form.submit()

    assert resp.status_code == 302
    assert (
        resp.location == "http://localhost/lectures/an/15/269/PO717460/amendements/list"
    )

    resp = resp.follow()

    assert resp.status_code == 200
    assert "2 réponses chargées" in resp.text

    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.avis == "Défavorable"
    assert amendement.position == 1
    assert "<strong>ipsum</strong>" in amendement.observations
    assert "<blink>amet</blink>" not in amendement.observations

    assert "<i>tempor</i>" in amendement.reponse
    assert "<u>aliqua</u>" not in amendement.reponse

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
    assert amendement.observations.startswith("Lorem")
    assert amendement.position == 2


def test_post_form_updates_modification_date(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.get(
            chambre=dummy_lecture[0],
            session=dummy_lecture[1],
            num_texte=dummy_lecture[2],
        )
        initial_modified_at = lecture.modified_at

    form = app.get("/lectures/an/15/269/amendements/list").form
    path = Path(__file__).parent / "sample_data" / "reponses.csv"
    form["reponses"] = Upload("file.csv", path.read_bytes())
    form.submit()

    with transaction.manager:
        lecture = Lecture.get(
            chambre=dummy_lecture[0],
            session=dummy_lecture[1],
            num_texte=dummy_lecture[2],
        )
        assert lecture.modified_at != initial_modified_at


def test_post_form_semicolumns(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession, Amendement

    form = app.get("/lectures/an/15/269/PO717460/amendements/list").form
    path = Path(__file__).parent / "sample_data" / "reponses_semicolumns.csv"
    form["reponses"] = Upload("file.csv", path.read_bytes())

    resp = form.submit()

    assert resp.status_code == 302
    assert (
        resp.location == "http://localhost/lectures/an/15/269/PO717460/amendements/list"
    )

    resp = resp.follow()

    assert resp.status_code == 200
    assert "2 réponses chargées" in resp.text

    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.avis == "Défavorable"
    assert amendement.position == 1
    assert "<strong>ipsum</strong>" in amendement.observations
    assert "<blink>amet</blink>" not in amendement.observations

    assert "<i>tempor</i>" in amendement.reponse
    assert "<u>aliqua</u>" not in amendement.reponse

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
    assert amendement.observations.startswith("Lorem")
    assert amendement.position == 2


def test_post_form_with_bom(app, dummy_lecture, dummy_amendements):
    form = app.get("/lectures/an/15/269/PO717460/amendements/list").form
    path = Path(__file__).parent / "sample_data" / "reponses_with_bom.csv"
    form["reponses"] = Upload("file.csv", path.read_bytes())

    resp = form.submit()

    assert resp.status_code == 302
    assert (
        resp.location == "http://localhost/lectures/an/15/269/PO717460/amendements/list"
    )

    resp = resp.follow()

    assert resp.status_code == 200
    assert "2 réponses chargées" in resp.text


def test_post_form_reponse_no_file(app, dummy_lecture, dummy_amendements):

    form = app.get("/lectures/an/15/269/PO717460/amendements/list").form
    resp = form.submit()

    assert resp.status_code == 302
    assert (
        resp.location == "http://localhost/lectures/an/15/269/PO717460/amendements/list"
    )

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Veuillez d’abord sélectionner un fichier" in resp.text
