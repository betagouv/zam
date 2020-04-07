from datetime import date

from webtest.forms import Select


def test_conseils_empty(app, user_david):
    resp = app.get("/conseils/", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert "Aucun conseil pour l’instant." in resp.text
    assert "Ajouter un conseil" in resp.text


def test_conseils_other_chambre(app, conseil_ccfp, user_csfpe):
    resp = app.get("/conseils/", user=user_csfpe)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert "Aucun conseil pour l’instant." in resp.text
    assert "Ajouter un conseil" in resp.text


def test_conseils(app, conseil_ccfp, user_ccfp):
    resp = app.get("/conseils/", user=user_ccfp)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert len(resp.parser.css(".conseil nav a")) == 1
    assert "Ajouter un conseil" in resp.text


def test_conseils_add_form_ccfp(app, user_ccfp):
    resp = app.get("/conseils/add", user=user_ccfp)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    form = resp.forms["add-conseil"]
    assert form.method == "POST"
    assert form.action == "/conseils/add"

    assert list(form.fields.keys()) == [
        "chambre",
        "date",
        "formation",
        "urgence_declaree",
        "submit",
    ]

    assert isinstance(form.fields["chambre"][0], Select)
    assert form.fields["chambre"][0].options == [
        ("", True, "Choisir dans la liste…"),
        ("CCFP", False, "Conseil commun de la fonction publique (CCFP)"),
    ]

    assert isinstance(form.fields["formation"][0], Select)
    assert form.fields["formation"][0].options == [
        ("ASSEMBLEE_PLENIERE", False, "Assemblée plénière"),
        ("FORMATION_SPECIALISEE", False, "Formation spécialisée"),
    ]

    assert form.fields["submit"][0].attrs["type"] == "submit"


def test_conseils_add_form_csfpe(app, user_csfpe):
    resp = app.get("/conseils/add", user=user_csfpe)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    form = resp.forms["add-conseil"]
    assert isinstance(form.fields["chambre"][0], Select)
    assert form.fields["chambre"][0].options == [
        ("", True, "Choisir dans la liste…"),
        ("CSFPE", False, "Conseil supérieur de la fonction publique d’État (CSFPE)"),
    ]


def test_conseils_add_submit(app, user_ccfp):
    from zam_repondeur.models import DBSession
    from zam_repondeur.visam.models import Conseil

    resp = app.get("/conseils/add", user=user_ccfp)
    form = resp.forms["add-conseil"]
    form["chambre"] = "CCFP"
    form["date"] = "2020-04-01"
    form["formation"] = "ASSEMBLEE_PLENIERE"
    form["urgence_declaree"] = "0"
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "https://visam.test/conseils/ccfp-2020-04-01"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Conseil créé avec succès." in resp.text

    conseil = DBSession.query(Conseil).one()
    assert conseil.chambre.value == "Conseil commun de la fonction publique"
    assert conseil.date == date(2020, 4, 1)
    assert conseil.formation.value == "Assemblée plénière"
    assert not conseil.urgence_declaree
    assert conseil.team.name == "ccfp-2020-04-01"


def test_conseils_add_submit_existing(app, conseil_ccfp, user_ccfp):
    from zam_repondeur.models import DBSession
    from zam_repondeur.visam.models import Conseil

    resp = app.get("/conseils/add", user=user_ccfp)
    form = resp.forms["add-conseil"]
    form["chambre"] = "CCFP"
    form["date"] = "2020-04-01"
    form["formation"] = "ASSEMBLEE_PLENIERE"
    form["urgence_declaree"] = "0"
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "https://visam.test/conseils/ccfp-2020-04-01"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Ce conseil existe déjà…" in resp.text

    assert len(DBSession.query(Conseil).all()) == 1
