from pathlib import Path

import transaction
from webtest import Upload

HERE = Path(__file__)
SAMPLE_DATA = HERE.parent.parent / "services" / "import_export" / "sample_data"


def test_get_form(
    app, lecture_essoc2018_an_nouvelle_lecture_commission_fond, user_david
):
    resp = app.get(
        "/dossiers/etat-service-societe-confiance/lectures/an.15.806.PO744107/options",
        user=user_david,
    )

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    form = resp.forms["import-liasse-xml"]

    assert form.method == "post"
    assert form.action == (
        "https://zam.test/"
        "dossiers/etat-service-societe-confiance/"
        "lectures/an.15.806.PO744107/"
        "import_liasse_xml"
    )

    assert list(form.fields.keys()) == ["liasse", "upload"]

    assert form.fields["liasse"][0].attrs["type"] == "file"
    assert form.fields["upload"][0].attrs["type"] == "submit"


def test_upload_liasse_success(
    app, lecture_essoc2018_an_nouvelle_lecture_commission_fond, user_david
):
    from zam_repondeur.models import DBSession, Lecture

    with transaction.manager:
        DBSession.add(user_david)

    resp = app.get(
        "/dossiers/etat-service-societe-confiance/lectures/an.15.806.PO744107/options",
        user=user_david,
    )
    form = resp.forms["import-liasse-xml"]
    form["liasse"] = Upload("liasse.xml", (SAMPLE_DATA / "liasse.xml").read_bytes())
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test/"
        "dossiers/etat-service-societe-confiance/"
        "lectures/an.15.806.PO744107/"
        "amendements/"
    )

    resp = resp.follow()
    assert "3 nouveaux amendements récupérés (import liasse XML)." in resp.text

    lecture = Lecture.get_by_pk(
        lecture_essoc2018_an_nouvelle_lecture_commission_fond.pk
    )
    assert lecture.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> a importé "
        "une liasse XML : 3 nouveaux amendements récupérés."
    )


def test_upload_liasse_with_table(
    app, lecture_essoc2018_an_nouvelle_lecture_commission_fond, user_david
):
    from zam_repondeur.models import Lecture

    resp = app.get(
        "/dossiers/etat-service-societe-confiance/lectures/an.15.806.PO744107/options",
        user=user_david,
    )
    form = resp.forms["import-liasse-xml"]
    form["liasse"] = Upload(
        "liasse.xml", (SAMPLE_DATA / "liasse_with_table.xml").read_bytes()
    )
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test/"
        "dossiers/etat-service-societe-confiance/"
        "lectures/an.15.806.PO744107/"
        "amendements/"
    )

    resp = resp.follow()
    assert "3 nouveaux amendements récupérés (import liasse XML)." in resp.text

    lecture = Lecture.get_by_pk(
        lecture_essoc2018_an_nouvelle_lecture_commission_fond.pk
    )
    assert (
        "<table>\n<tbody>\n<tr>\n<td>Durée minimale de services"
        in lecture.amendements[1].corps
    )
    assert (
        "<table>\n<tbody>\n<tr>\n<td>Durée minimale de services"
        in lecture.amendements[0].expose
    )


def test_upload_liasse_success_with_a_deposer(
    app, lecture_essoc2018_an_nouvelle_lecture_commission_fond, user_david
):
    resp = app.get(
        "/dossiers/etat-service-societe-confiance/lectures/an.15.806.PO744107/options",
        user=user_david,
    )
    form = resp.forms["import-liasse-xml"]
    # The second amendement has `etat == "A déposer"` and thus is ignored.
    form["liasse"] = Upload(
        "liasse.xml", (SAMPLE_DATA / "liasse_with_a_deposer.xml").read_bytes()
    )
    resp = form.submit()
    resp = resp.follow()
    assert "2 nouveaux amendements récupérés (import liasse XML)." in resp.text


def test_upload_liasse_missing_file(
    app, lecture_essoc2018_an_nouvelle_lecture_commission_fond, user_david
):
    from zam_repondeur.models import Lecture

    resp = app.get(
        "/dossiers/etat-service-societe-confiance/lectures/an.15.806.PO744107/options",
        user=user_david,
    )
    form = resp.forms["import-liasse-xml"]
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test/"
        "dossiers/etat-service-societe-confiance/"
        "lectures/an.15.806.PO744107/"
        "options"
    )

    resp = resp.follow()
    assert "Veuillez d’abord sélectionner un fichier" in resp.text

    # Check the update timestamp has NOT been updated.
    lecture = Lecture.get_by_pk(
        lecture_essoc2018_an_nouvelle_lecture_commission_fond.pk
    )
    assert lecture.events == []
