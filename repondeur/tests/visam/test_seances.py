from datetime import date

from webtest.forms import Select


def test_seances_empty(app, user_david):
    resp = app.get("/seances/", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert "Aucune séance pour l’instant." in resp.text
    assert "Ajouter une séance" not in resp.text


def test_seances_other_chambre_user(app, seance_ccfp, user_csfpe):
    resp = app.get("/seances/", user=user_csfpe)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert "Aucune séance pour l’instant." in resp.text
    assert "Ajouter une séance" not in resp.text


def test_seances_admin_user(app, seance_ccfp, user_admin):
    resp = app.get("/seances/", user=user_admin)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert len(resp.parser.css(".seance nav a")) == 1
    assert "Ajouter une séance" in resp.text


def test_seances(app, seance_ccfp, user_ccfp):
    resp = app.get("/seances/", user=user_ccfp)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert len(resp.parser.css(".seance nav a")) == 1
    assert "Ajouter une séance" not in resp.text


def test_seances_add_form_no_admin(app, user_ccfp):
    resp = app.get("/seances/add", user=user_ccfp)
    assert resp.status_code == 302

    resp = resp.maybe_follow()
    assert "L’accès à cette page est réservé aux personnes autorisées." in resp.text


def test_seances_add_form(app, user_admin):
    resp = app.get("/seances/add", user=user_admin)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    form = resp.forms["add-seance"]
    assert form.method == "POST"
    assert form.action == "/seances/add"

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
        ("CSFPE", False, "Conseil supérieur de la fonction publique d’État (CSFPE)"),
    ]

    assert isinstance(form.fields["formation"][0], Select)
    assert form.fields["formation"][0].options == [
        ("ASSEMBLEE_PLENIERE", False, "Assemblée plénière"),
        ("FORMATION_SPECIALISEE", False, "Formation spécialisée"),
    ]

    assert form.fields["submit"][0].attrs["type"] == "submit"


def test_seances_add_submit(app, user_admin):
    from zam_repondeur.models import DBSession
    from zam_repondeur.visam.models import Seance

    resp = app.get("/seances/add", user=user_admin)
    form = resp.forms["add-seance"]
    form["chambre"] = "CCFP"
    form["date"] = "2020-04-01"
    form["formation"] = "ASSEMBLEE_PLENIERE"
    form["urgence_declaree"] = "0"
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "https://visam.test/seances/ccfp-2020-04-01"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Séance créée avec succès." in resp.text

    seance = DBSession.query(Seance).one()
    assert seance.chambre.value == "Conseil commun de la fonction publique"
    assert seance.date == date(2020, 4, 1)
    assert seance.formation.value == "Assemblée plénière"
    assert not seance.urgence_declaree
    assert seance.team.name == "ccfp-2020-04-01"


def test_seances_add_submit_existing(app, seance_ccfp, user_admin):
    from zam_repondeur.models import DBSession
    from zam_repondeur.visam.models import Seance

    resp = app.get("/seances/add", user=user_admin)
    form = resp.forms["add-seance"]
    form["chambre"] = "CCFP"
    form["date"] = "2020-04-01"
    form["formation"] = "ASSEMBLEE_PLENIERE"
    form["urgence_declaree"] = "0"
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "https://visam.test/seances/ccfp-2020-04-01"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Cette séance existe déjà…" in resp.text

    assert len(DBSession.query(Seance).all()) == 1