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
