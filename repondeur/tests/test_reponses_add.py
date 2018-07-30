import transaction
from pathlib import Path

from webtest import Upload
from webtest.forms import File


def test_get_form(app, dummy_lecture):
    resp = app.get("/lectures/an.15.269.PO717460/amendements/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    assert resp.forms["import-form"].method == "post"
    assert resp.forms["import-form"].action == ""

    assert list(resp.forms["import-form"].fields.keys()) == ["reponses", "upload"]

    assert isinstance(resp.forms["import-form"].fields["reponses"][0], File)
    assert resp.forms["import-form"].fields["upload"][0].attrs["type"] == "submit"


def test_post_form(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession, Amendement

    form = app.get("/lectures/an.15.269.PO717460/amendements/").forms["import-form"]
    path = Path(__file__).parent / "sample_data" / "reponses.csv"
    form["reponses"] = Upload("file.csv", path.read_bytes())

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

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
        initial_modified_at = dummy_lecture.modified_at

    form = app.get("/lectures/an.15.269.PO717460/amendements/").forms["import-form"]
    path = Path(__file__).parent / "sample_data" / "reponses.csv"
    form["reponses"] = Upload("file.csv", path.read_bytes())
    form.submit()

    with transaction.manager:
        lecture = Lecture.get(
            chambre=dummy_lecture.chambre,
            session=dummy_lecture.session,
            num_texte=dummy_lecture.num_texte,
            organe=dummy_lecture.organe,
        )
        assert lecture.modified_at != initial_modified_at


def test_post_form_semicolumns(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import DBSession, Amendement

    form = app.get("/lectures/an.15.269.PO717460/amendements/").forms["import-form"]
    path = Path(__file__).parent / "sample_data" / "reponses_semicolumns.csv"
    form["reponses"] = Upload("file.csv", path.read_bytes())

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

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
    form = app.get("/lectures/an.15.269.PO717460/amendements/").forms["import-form"]
    path = Path(__file__).parent / "sample_data" / "reponses_with_bom.csv"
    form["reponses"] = Upload("file.csv", path.read_bytes())

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "2 réponses chargées" in resp.text


def test_post_form_wrong_columns_names(app, dummy_lecture, dummy_amendements):
    form = app.get("/lectures/an.15.269.PO717460/amendements").forms["import-form"]
    path = Path(__file__).parent / "sample_data" / "reponses_wrong_columns_names.csv"
    form["reponses"] = Upload("file.csv", path.read_bytes())

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert (
        "2 réponses n’ont pas pu être chargées. Pour rappel, il faut que le fichier "
        "CSV contienne au moins les noms de colonnes suivants « Nº amdt », "
        "« Avis du Gouvernement », « Objet amdt » et « Réponse »." in resp.text
    )


def test_post_form_reponse_no_file(app, dummy_lecture, dummy_amendements):

    form = app.get("/lectures/an.15.269.PO717460/amendements/").forms["import-form"]
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Veuillez d’abord sélectionner un fichier" in resp.text


def test_post_form_from_export(
    app, dummy_lecture, dummy_amendements_with_reponses, tmpdir
):
    from zam_repondeur.models import DBSession, Amendement
    from zam_repondeur.writer import write_csv

    filename = str(tmpdir.join("test.csv"))

    nb_rows = write_csv("Titre", dummy_amendements_with_reponses, filename, request={})

    assert nb_rows == 2

    with transaction.manager:
        dummy_amendements_with_reponses[0].avis = None
        dummy_amendements_with_reponses[1].avis = None

    form = app.get("/lectures/an.15.269.PO717460/amendements/").forms["import-form"]
    form["reponses"] = Upload("file.csv", Path(filename).read_bytes())

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "2 réponses chargées" in resp.text

    amendement = DBSession.query(Amendement).filter(Amendement.num == 333).first()
    assert amendement.avis == "Favorable"
    amendement = DBSession.query(Amendement).filter(Amendement.num == 777).first()
    assert amendement.avis == "Favorable"
