import os

from webtest.forms import Select


def test_get_form(app):

    resp = app.get("/textes/add")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    assert resp.form.method == "POST"
    assert resp.form.action == "/textes/add"

    assert list(resp.form.fields.keys()) == [
        "chambre",
        "session",
        "num_texte",
        "submit",
    ]

    assert isinstance(resp.form.fields["chambre"][0], Select)
    assert resp.form.fields["chambre"][0].options == [("senat", True, "Sénat")]

    assert isinstance(resp.form.fields["session"][0], Select)
    assert resp.form.fields["session"][0].options == [("2017-2018", True, "2017-2018")]

    assert resp.form.fields["num_texte"][0].attrs["type"] == "number"

    assert resp.form.fields["submit"][0].attrs["type"] == "submit"


def test_post_form(app, tmpdir):
    form = app.get("/textes/add").form
    form["chambre"] = "senat"
    form["session"] = "2017-2018"
    form["num_texte"] = "63"

    assert not os.path.isdir(tmpdir.join("zam").join("senat-2017-2018-63"))

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/textes/"

    assert os.path.isdir(tmpdir.join("zam").join("senat-2017-2018-63"))


def test_post_form_bad_chambre(app):
    resp = app.post(
        "/textes/add",
        {"chambre": "assemblee", "session": "2017-2018", "num_texte": "63"},
        expect_errors=True,
    )
    assert resp.status_code == 400  # Bad request
