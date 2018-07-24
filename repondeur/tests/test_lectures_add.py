from webtest.forms import Select


def test_get_form(app):
    resp = app.get("/lectures/add")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    form = resp.forms["add-lecture"]
    assert form.method == "POST"
    assert form.action == "/lectures/add"

    assert list(form.fields.keys()) == ["dossier", "lecture", "submit"]

    assert isinstance(form.fields["dossier"][0], Select)
    assert form.fields["dossier"][0].options == [
        ("", True, ""),
        ("DLR5L15N36030", False, "Sécurité sociale : loi de financement 2018"),
    ]

    assert isinstance(form.fields["lecture"][0], Select)
    assert form.fields["lecture"][0].options == [("", True, "")]

    assert form.fields["submit"][0].attrs["type"] == "submit"


def test_post_form(app):
    from zam_repondeur.models import Lecture

    assert not Lecture.exists(
        chambre="an", session="15", num_texte=269, organe="PO717460"
    )

    # We cannot use form.submit() given the form is dynamic and does not
    # contain choices for lectures (dynamically loaded via JS).
    resp = app.post(
        "/lectures/add",
        {"dossier": "DLR5L15N36030", "lecture": "PRJLANR5L15B0269-PO717460"},
    )

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an/15/269/PO717460/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Lecture créée avec succès." in resp.text

    lecture = Lecture.get(chambre="an", session="15", num_texte=269, organe="PO717460")
    assert lecture.chambre == "an"
    assert lecture.titre == "1ère lecture"
    assert lecture.dossier_legislatif == "Sécurité sociale : loi de financement 2018"


def test_post_form_already_exists(app, dummy_lecture):
    from zam_repondeur.models import Lecture

    assert Lecture.exists(chambre="an", session="15", num_texte=269, organe="PO717460")

    # We cannot use form.submit() given the form is dynamic and does not
    # contain choices for lectures (dynamically loaded via JS).
    resp = app.post(
        "/lectures/add",
        {"dossier": "DLR5L15N36030", "lecture": "PRJLANR5L15B0269-PO717460"},
    )

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an/15/269/PO717460/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Cette lecture existe déjà..." in resp.text


def test_choices_lectures(app):

    resp = app.get("/choices/dossiers/DLR5L15N36030/")

    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/json"
    assert resp.json == {
        "lectures": [
            {
                "key": "PRJLANR5L15B0269-PO717460",
                "label": "Assemblée nationale – 1ère lecture – Texte Nº 269",
            }
        ]
    }
