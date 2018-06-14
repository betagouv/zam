from webtest.forms import Select


def test_get_form(app):

    resp = app.get("/lectures/add")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    assert resp.form.method == "POST"
    assert resp.form.action == "/lectures/add"

    assert list(resp.form.fields.keys()) == [
        "chambre",
        "session",
        "num_texte",
        "submit",
    ]

    assert isinstance(resp.form.fields["chambre"][0], Select)
    assert resp.form.fields["chambre"][0].options == [
        ("an", True, "Assemblée nationale"),
        ("senat", False, "Sénat"),
    ]

    assert isinstance(resp.form.fields["session"][0], Select)
    assert resp.form.fields["session"][0].options == [
        ("15", True, "15e législature"),
        ("14", False, "14e législature"),
    ]

    assert resp.form.fields["num_texte"][0].attrs["type"] == "number"

    assert resp.form.fields["submit"][0].attrs["type"] == "submit"


def test_post_form(app):
    from zam_repondeur.models import Lecture

    form = app.get("/lectures/add").form
    form["chambre"] = "an"
    form["session"] = "15"
    form["num_texte"] = "269"

    assert not Lecture.exists(chambre="an", session="15", num_texte="0269")

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an/15/0269/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Lecture créée avec succès." in resp.text

    assert Lecture.exists(chambre="an", session="15", num_texte="0269")


def test_post_form_already_exists(app, dummy_lecture):
    from zam_repondeur.models import Lecture

    assert Lecture.exists(chambre="an", session="15", num_texte="0269")

    form = app.get("/lectures/add").form
    form["chambre"] = "an"
    form["session"] = "15"
    form["num_texte"] = "269"

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an/15/0269/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Cette lecture existe déjà..." in resp.text


def test_post_form_bad_chambre(app):
    resp = app.post(
        "/lectures/add",
        {"chambre": "tralala", "session": "2017-2018", "num_texte": "63"},
        expect_errors=True,
    )
    assert resp.status_code == 400  # Bad request
