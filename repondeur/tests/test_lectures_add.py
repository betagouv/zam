from webtest.forms import Select


def test_get_form(app):
    resp = app.get("/lectures/add")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    assert resp.form.method == "POST"
    assert resp.form.action == "/lectures/add"

    assert list(resp.form.fields.keys()) == ["dossier", "lecture", "submit"]

    assert isinstance(resp.form.fields["dossier"][0], Select)
    assert resp.form.fields["dossier"][0].options == [("", True, "")]

    assert isinstance(resp.form.fields["lecture"][0], Select)
    assert resp.form.fields["lecture"][0].options == [("", True, "")]

    assert resp.form.fields["submit"][0].attrs["type"] == "submit"


def test_post_form(app):
    from zam_repondeur.models import Lecture

    form = app.get("/lectures/add").form
    form["dossier"] = "DLR5L15N36030"
    form["lecture"] = "0"

    assert not Lecture.exists(
        chambre="an", session="15", num_texte=269, organe="PO717460"
    )

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an/15/269/PO717460/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Lecture créée avec succès." in resp.text

    lecture = Lecture.get(chambre="an", session="15", num_texte=269, organe="PO717460")
    assert lecture.chambre == "an"
    assert lecture.titre == "1ère lecture"


def test_post_form_already_exists(app, dummy_lecture):
    from zam_repondeur.models import Lecture

    assert Lecture.exists(chambre="an", session="15", num_texte=269, organe="PO717460")

    form = app.get("/lectures/add").form
    form["dossier"] = "DLR5L15N36030"
    form["lecture"] = "0"

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an/15/269/PO717460/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Cette lecture existe déjà..." in resp.text
