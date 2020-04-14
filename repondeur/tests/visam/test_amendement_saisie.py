class TestButtonToAddAmendementOnIndex:
    def test_ccfp(self, app, user_ccfp, seance_ccfp, lecture_seance_ccfp):
        lecture = lecture_seance_ccfp
        dossier = lecture.dossier
        resp = app.get(
            f"/seances/{seance_ccfp.slug}/textes/{dossier.slug}/amendements/",
            user=user_ccfp,
        )
        assert resp.status_code == 200
        assert "Aucun amendement saisi pour l’instant…" in resp
        assert "Saisir un nouvel amendement" in resp

    def test_csfpe(self, app, user_csfpe, seance_csfpe, lecture_seance_csfpe):
        lecture = lecture_seance_csfpe
        dossier = lecture.dossier
        resp = app.get(
            f"/seances/{seance_csfpe.slug}/textes/{dossier.slug}/amendements/",
            user=user_csfpe,
        )
        assert resp.status_code == 200
        assert "Aucun amendement saisi pour l’instant…" in resp
        assert "Saisir un nouvel amendement" in resp


class TestAmendementSaisieForm:
    def test_get_form(
        self, app, seance_ccfp, lecture_seance_ccfp, amendements_an, user_ccfp
    ):
        resp = app.get(
            (
                f"/seances/{seance_ccfp.slug}"
                f"/textes/{lecture_seance_ccfp.dossier.slug}/amendements/saisie"
            ),
            user=user_ccfp,
        )

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

    def test_post_form(
        self,
        app,
        seance_ccfp,
        lecture_seance_ccfp,
        article1_texte_seance_ccfp,
        user_ccfp,
    ):
        from zam_repondeur.models import Amendement, DBSession

        assert len(DBSession.query(Amendement).all()) == 0

        resp = app.get(
            (
                f"/seances/{seance_ccfp.slug}"
                f"/textes/{lecture_seance_ccfp.dossier.slug}/amendements/saisie"
            ),
            user=user_ccfp,
        )
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
            "https://visam.test/seances/ccfp-2020-04-01/"
            "textes/titre-texte-ccfp/amendements/#amdt-CFTC-1"
        )

        amendement = DBSession.query(Amendement).first()
        assert amendement.groupe == "CFTC"
        assert amendement.article.pk == article1_texte_seance_ccfp.pk
        assert amendement.corps == "Un corps de rêve"
        assert (
            amendement.expose
            == "Avec un <table><tbody><tr><td>exposé</td></tr></tbody></table>"
        )
