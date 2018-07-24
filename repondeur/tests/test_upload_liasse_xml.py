from pathlib import Path

import pytest
import transaction
from webtest import Upload


SAMPLE_LIASSE = Path(__file__).parent / "sample_data" / "liasse.xml"


@pytest.fixture
def dummy_lecture_essoc(app):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            num_texte=806,
            titre="Nouvelle lecture",
            organe="PO744107",
            dossier_legislatif="Fonction publique : un Etat au service d'une société de confiance",  # noqa
        )

    return lecture


def test_get_form(app, dummy_lecture_essoc):
    resp = app.get("/lectures/an.15.806.PO744107/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    form = resp.forms["import-liasse-xml"]

    assert form.method == "post"
    assert (
        form.action == "http://localhost/lectures/an.15.806.PO744107/import_liasse_xml"
    )

    assert list(form.fields.keys()) == ["liasse", "upload"]

    assert form.fields["liasse"][0].attrs["type"] == "file"
    assert form.fields["upload"][0].attrs["type"] == "submit"


def test_upload_liasse_success(app, dummy_lecture_essoc):
    resp = app.get("/lectures/an.15.806.PO744107/")
    form = resp.forms["import-liasse-xml"]
    form["liasse"] = Upload("liasse.xml", SAMPLE_LIASSE.read_bytes())
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.806.PO744107/"

    resp = resp.follow()
    # print(resp.text)
    assert "2 nouveaux amendements récupérés." in resp.text


def test_upload_liasse_missing_file(app, dummy_lecture_essoc):
    resp = app.get("/lectures/an.15.806.PO744107/")
    form = resp.forms["import-liasse-xml"]
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.806.PO744107/"

    resp = resp.follow()
    assert "Veuillez d’abord sélectionner un fichier" in resp.text
