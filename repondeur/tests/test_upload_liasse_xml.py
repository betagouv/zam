from pathlib import Path

import pytest
import transaction
from webtest import Upload


SAMPLE_LIASSE = Path(__file__).parent / "sample_data" / "liasse.xml"


@pytest.fixture
def lecture_essoc(app):
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


def test_get_form(app, lecture_essoc):
    resp = app.get("/lectures/an.15.806.PO744107/amendements")

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


def test_upload_liasse_success(app, lecture_essoc):
    from zam_repondeur.models import DBSession, Journal, Lecture

    with transaction.manager:
        initial_modified_at = lecture_essoc.modified_at

    resp = app.get("/lectures/an.15.806.PO744107/amendements")
    form = resp.forms["import-liasse-xml"]
    form["liasse"] = Upload("liasse.xml", SAMPLE_LIASSE.read_bytes())
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.806.PO744107/amendements"

    resp = resp.follow()
    assert "3 nouveaux amendements récupérés (import liasse XML)." in resp.text

    # Check the update timestamp has been updated.
    with transaction.manager:
        lecture = Lecture.get(
            chambre=lecture_essoc.chambre,
            session=lecture_essoc.session,
            num_texte=lecture_essoc.num_texte,
            organe=lecture_essoc.organe,
        )
        assert lecture.modified_at != initial_modified_at

    assert (
        DBSession.query(Journal).first().message
        == "3 nouveaux amendements récupérés (import liasse XML)."
    )


def test_upload_liasse_missing_file(app, lecture_essoc):
    from zam_repondeur.models import DBSession, Journal, Lecture

    with transaction.manager:
        initial_modified_at = lecture_essoc.modified_at

    resp = app.get("/lectures/an.15.806.PO744107/amendements")
    form = resp.forms["import-liasse-xml"]
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.806.PO744107/amendements"

    resp = resp.follow()
    assert "Veuillez d’abord sélectionner un fichier" in resp.text

    # Check the update timestamp has NOT been updated.
    with transaction.manager:
        lecture = Lecture.get(
            chambre=lecture_essoc.chambre,
            session=lecture_essoc.session,
            num_texte=lecture_essoc.num_texte,
            organe=lecture_essoc.organe,
        )
        assert lecture.modified_at == initial_modified_at

    assert DBSession.query(Journal).first() is None
