class TestWhitelistList:
    def test_only_accessible_to_admin(self, app, user_sgg):
        from zam_repondeur.models import AllowedEmailPattern, DBSession

        assert DBSession.query(AllowedEmailPattern).count() == 1

        resp = app.get("/whitelist/", user=user_sgg)

        assert resp.status_code == 200
        assert resp.content_type == "text/html"

        assert len(resp.parser.css(".box ul li")) == 1
        assert resp.parser.css(".box ul li")[0].text().strip() == "*@*.gouv.fr"

    def test_not_accessible_to_regular_user(self, app, user_david):
        resp = app.get("/whitelist/", user=user_david)

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/"


class TestWhitelistAdd:
    def test_create(self, app, user_sgg):
        from zam_repondeur.models import AllowedEmailPattern, DBSession

        assert DBSession.query(AllowedEmailPattern).count() == 1
        resp = app.get("/whitelist/add", user=user_sgg)

        form = resp.form
        form["email_pattern"] = "foo@example.com"

        resp = form.submit()

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/whitelist/"

        resp = resp.follow()

        assert resp.status_code == 200
        assert resp.content_type == "text/html"

        assert len(resp.parser.css(".box ul li")) == 2
        assert resp.parser.css(".box ul li")[0].text().strip() == "*@*.gouv.fr"
        assert resp.parser.css(".box ul li")[1].text().strip() == "foo@example.com"
        assert DBSession.query(AllowedEmailPattern).count() == 2

    def test_not_possible_to_regular_user(self, app, user_david):
        from zam_repondeur.models import AllowedEmailPattern, DBSession

        assert DBSession.query(AllowedEmailPattern).count() == 1

        resp = app.post(
            "/whitelist/add", {"email_pattern": "foo@bar.com"}, user=user_david
        )

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/"
        assert DBSession.query(AllowedEmailPattern).count() == 1


class TestWhitelistDelete:
    def test_delete(self, app, user_sgg):
        from zam_repondeur.models import AllowedEmailPattern, DBSession

        assert DBSession.query(AllowedEmailPattern).count() == 1
        existing_pattern = DBSession.query(AllowedEmailPattern).first()

        resp = app.get("/whitelist/", user=user_sgg)

        form = resp.form
        form["pk"] = existing_pattern.pk

        resp = form.submit()

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/whitelist/"

        resp = resp.follow()

        assert resp.status_code == 200
        assert resp.content_type == "text/html"

        assert len(resp.parser.css(".box ul li")) == 0
        assert DBSession.query(AllowedEmailPattern).count() == 0

    def test_not_possible_to_regular_user(self, app, user_david):
        from zam_repondeur.models import AllowedEmailPattern, DBSession

        assert DBSession.query(AllowedEmailPattern).count() == 1
        existing_pattern = DBSession.query(AllowedEmailPattern).first()

        resp = app.post("/whitelist/", {"pk": existing_pattern.pk}, user=user_david)

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/"
        assert DBSession.query(AllowedEmailPattern).count() == 1
