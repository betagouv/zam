from unittest.mock import patch

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


def test_post_form(app):
    form = app.get("/textes/add").form
    form["chambre"] = "senat"
    form["session"] = "2017-2018"
    form["num_texte"] = "63"

    with patch("zam_repondeur.views.textes.get_amendements_senat") as mock:
        mock.return_value = []
        resp = form.submit()

    mock.assert_called_once_with("2017-2018", "63")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"


def test_post_form_bad_chambre(app):
    resp = app.post(
        "/textes/add",
        {"chambre": "assemblee", "session": "2017-2018", "num_texte": "63"},
        expect_errors=True,
    )
    assert resp.status_code == 400  # Bad request
