from datetime import date

import pytest
from webtest.forms import Select


class TestListeSeances:
    def test_message_when_list_is_empty(self, app, user_gouvernement):
        resp = app.get("/seances/", user=user_gouvernement)

        assert resp.status_code == 200
        assert resp.content_type == "text/html"

        assert "Aucune séance pour l’instant." in resp.text

    @pytest.mark.usefixtures("seance_ccfp", "seance_csfpe")
    def test_gouvernement_sees_all_seances(self, app, user_gouvernement):
        resp = app.get("/seances/", user=user_gouvernement)

        assert resp.status_code == 200
        assert resp.content_type == "text/html"

        assert len(resp.parser.css(".seance nav a")) == 2

    @pytest.mark.usefixtures("seance_ccfp", "seance_csfpe")
    def test_admin_sees_all_seances(self, app, user_admin):
        resp = app.get("/seances/", user=user_admin)

        assert resp.status_code == 200
        assert resp.content_type == "text/html"

        assert len(resp.parser.css(".seance nav a")) == 2

    @pytest.mark.usefixtures("seance_ccfp", "seance_csfpe")
    def test_member_sees_only_seance_for_their_conseil(self, app, user_ccfp):
        resp = app.get("/seances/", user=user_ccfp)

        assert resp.status_code == 200
        assert resp.content_type == "text/html"

        assert len(resp.parser.css(".seance nav a")) == 1


class TestAddSeanceButton:
    def test_gouvernement_sees_the_button(self, app, user_gouvernement):
        resp = app.get("/seances/", user=user_gouvernement)
        assert "Ajouter une séance" in resp.text

    def test_admin_sees_the_button(self, app, user_admin):
        resp = app.get("/seances/", user=user_admin)
        assert "Ajouter une séance" in resp.text

    def test_member_does_not_see_the_button(self, app, user_ccfp):
        resp = app.get("/seances/", user=user_ccfp)
        assert "Ajouter une séance" not in resp.text


class TestSeanceAddGetForm:
    def test_member_cannot_access_the_form(self, app, user_ccfp):
        resp = app.get("/seances/add", user=user_ccfp)
        assert resp.status_code == 302

        resp = resp.maybe_follow()
        assert "L’accès à cette page est réservé aux personnes autorisées." in resp.text

    def test_gouvernement_can_access_the_form(self, app, user_gouvernement):
        resp = app.get("/seances/add", user=user_gouvernement)

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
            (
                "CSFPE",
                False,
                "Conseil supérieur de la fonction publique d’État (CSFPE)",
            ),
        ]

        assert isinstance(form.fields["formation"][0], Select)
        assert form.fields["formation"][0].options == [
            ("ASSEMBLEE_PLENIERE", False, "Assemblée plénière"),
            ("FORMATION_SPECIALISEE", False, "Formation spécialisée"),
        ]

        assert form.fields["submit"][0].attrs["type"] == "submit"


class TestSeanceAddSubmitForm:
    def test_member_cannot_submit_the_form(self, app, user_ccfp):
        resp = app.post(
            "/seances/add",
            {
                "chambre": "CCFP",
                "date": "2020-04-01",
                "formation": "ASSEMBLEE_PLENIERE",
                "urgence_declaree": "0",
            },
            user=user_ccfp,
        )
        assert resp.status_code == 302

        resp = resp.maybe_follow()
        assert "L’accès à cette page est réservé aux personnes autorisées." in resp.text

    def test_gouvernement_can_add_new_seance(self, app, user_gouvernement):
        from zam_repondeur.models import DBSession
        from zam_repondeur.visam.models import Seance

        resp = app.get("/seances/add", user=user_gouvernement)
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

    def test_gouvernement_cannot_add_duplicate_seance(
        self, app, seance_ccfp, user_gouvernement
    ):
        from zam_repondeur.models import DBSession
        from zam_repondeur.visam.models import Seance

        resp = app.get("/seances/add", user=user_gouvernement)
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
