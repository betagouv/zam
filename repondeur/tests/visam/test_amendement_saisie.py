from urllib.parse import quote


class TestButtonToAddAmendementOnIndex:
    def test_ccfp(self, app, user_david, lecture_conseil_ccfp):
        lecture = lecture_conseil_ccfp
        dossier = lecture.dossier
        resp = app.get(
            f"/dossiers/{dossier.slug}/lectures/{quote(lecture.url_key)}/amendements/",
            user=user_david,
        )
        assert resp.status_code == 200
        assert "Aucun amendement saisi pour l’instant…" in resp
        assert "Saisir un nouvel amendement" in resp

    def test_csfpe(self, app, user_david, lecture_conseil_csfpe):
        lecture = lecture_conseil_csfpe
        dossier = lecture.dossier
        resp = app.get(
            f"/dossiers/{dossier.slug}/lectures/{quote(lecture.url_key)}/amendements/",
            user=user_david,
        )
        assert resp.status_code == 200
        assert "Aucun amendement saisi pour l’instant…" in resp
        assert "Saisir un nouvel amendement" in resp


class TestAmendementSaisieForm:
    def test_get_form(self, app, lecture_an_url, amendements_an, user_david):
        resp = app.get(f"{lecture_an_url}/amendements/saisie", user=user_david,)

        assert resp.status_code == 200
        assert resp.content_type == "text/html"

        assert resp.forms["saisie-amendement"].method == "POST"
        assert list(resp.forms["saisie-amendement"].fields.keys()) == [
            "subdiv",
            "groupe",
            "corps",
            "expose",
            "save",
        ]

    def test_post_form(self, app, lecture_an_url, article1_an, user_david):
        from zam_repondeur.models import Amendement, DBSession

        assert len(DBSession.query(Amendement).all()) == 0

        resp = app.get(f"{lecture_an_url}/amendements/saisie", user=user_david)
        form = resp.forms["saisie-amendement"]
        form["subdiv"] = "article.1.."
        form["groupe"] = "CFTC"
        form[
            "corps"
        ] = 'Un corps <span style="font-family: Arial Narrow, serif;">de</span> rêve'
        form["expose"] = "Avec un <table><tr><td>exposé</td></tr></table>"
        resp = form.submit("save")

        assert resp.status_code == 302
        assert resp.location == (
            "https://visam.test/"
            "dossiers/plfss-2018/"
            "lectures/an.15.269.PO717460/"
            "amendements/#amdt-CFTC-1"
        )

        amendement = DBSession.query(Amendement).first()
        assert amendement.groupe == "CFTC"
        assert amendement.article.pk == article1_an.pk
        assert amendement.corps == "Un corps de rêve"
        assert (
            amendement.expose
            == "Avec un <table><tbody><tr><td>exposé</td></tr></tbody></table>"
        )
