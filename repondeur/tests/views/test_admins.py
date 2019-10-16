from datetime import datetime

import transaction


class TestAdminList:
    def test_only_accessible_to_admin(self, app, user_sgg):
        from zam_repondeur.models import User, DBSession

        assert DBSession.query(User).filter(User.admin_at.isnot(None)).count() == 1

        resp = app.get("/admins/", user=user_sgg)

        assert resp.status_code == 200
        assert resp.content_type == "text/html"

        assert len(resp.parser.css(".box ul li")) == 1
        assert (
            resp.parser.css(".box ul li")[0].text().strip()
            == "SGG user (user@sgg.pm.gouv.fr)"
        )

    def test_not_accessible_to_regular_user(self, app, user_david):
        resp = app.get("/admins/", user=user_david)

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/"


class TestAdminAdd:
    def test_create(self, app, user_sgg, user_david):
        from zam_repondeur.models import User, DBSession

        assert DBSession.query(User).filter(User.admin_at.isnot(None)).count() == 1
        resp = app.get("/admins/add", user=user_sgg)

        form = resp.form
        form["user_pk"] = user_david.pk

        resp = form.submit()

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/admins/"

        resp = resp.follow()

        assert resp.status_code == 200
        assert resp.content_type == "text/html"

        assert len(resp.parser.css(".box ul li")) == 2
        assert (
            resp.parser.css(".box ul li")[0].text().strip()
            == "SGG user (user@sgg.pm.gouv.fr)"
        )
        assert (
            resp.parser.css(".box ul li")[1].text().strip()
            == "David (david@exemple.gouv.fr)"
        )
        assert DBSession.query(User).filter(User.admin_at.isnot(None)).count() == 2

        with transaction.manager:
            DBSession.add(user_sgg)
            assert len(user_sgg.events) == 1
            assert user_sgg.events[0].render_summary() == (
                "<abbr title='user@sgg.pm.gouv.fr'>SGG user</abbr> a ajouté "
                "<abbr title='david@exemple.gouv.fr'>David (david@exemple.gouv.fr)"
                "</abbr> à la liste des administrateur·ice·s."
            )

    def test_submit_empty(self, app, user_sgg, user_david):
        from zam_repondeur.models import User, DBSession

        assert DBSession.query(User).filter(User.admin_at.isnot(None)).count() == 1
        resp = app.get("/admins/add", user=user_sgg)

        form = resp.form
        form["user_pk"] = ""
        resp = form.submit()

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/admins/add"

        resp = resp.follow()

        assert resp.status_code == 200
        assert resp.content_type == "text/html"
        assert "Veuillez saisir une personne dans le menu déroulant." in resp.text

    def test_not_possible_to_regular_user(self, app, user_sgg, user_david):
        from zam_repondeur.models import User, DBSession

        assert DBSession.query(User).filter(User.admin_at.isnot(None)).count() == 1

        resp = app.post("/admins/add", {"user_pk": user_david.pk}, user=user_david)

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/"
        assert DBSession.query(User).filter(User.admin_at.isnot(None)).count() == 1


class TestAdminDelete:
    def test_delete(self, app, user_sgg, user_david):
        from zam_repondeur.models import User, DBSession

        with transaction.manager:
            user_david.admin_at = datetime.utcnow()
            DBSession.add(user_david)

        assert DBSession.query(User).filter(User.admin_at.isnot(None)).count() == 2

        resp = app.get("/admins/", user=user_sgg)

        form = resp.forms[1]
        form["user_pk"] = user_david.pk

        resp = form.submit()

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/admins/"

        resp = resp.follow()

        assert resp.status_code == 200
        assert resp.content_type == "text/html"

        assert len(resp.parser.css(".box ul li")) == 1
        assert DBSession.query(User).filter(User.admin_at.isnot(None)).count() == 1

        with transaction.manager:
            DBSession.add(user_sgg)
            assert len(user_sgg.events) == 1
            assert user_sgg.events[0].render_summary() == (
                "<abbr title='user@sgg.pm.gouv.fr'>SGG user</abbr> a retiré "
                "<abbr title='david@exemple.gouv.fr'>David (david@exemple.gouv.fr)"
                "</abbr> de la liste des administrateur·ice·s."
            )

    def test_not_possible_to_regular_user(self, app, user_sgg, user_david, user_ronan):
        from zam_repondeur.models import User, DBSession

        with transaction.manager:
            user_david.admin_at = datetime.utcnow()
            DBSession.add(user_david)
        assert DBSession.query(User).filter(User.admin_at.isnot(None)).count() == 2

        resp = app.post("/admins/", {"user_pk": user_david.pk}, user=user_ronan)

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/"
        assert DBSession.query(User).filter(User.admin_at.isnot(None)).count() == 2

    def test_not_possible_to_yourself(self, app, user_sgg, user_david):
        from zam_repondeur.models import User, DBSession

        with transaction.manager:
            user_david.admin_at = datetime.utcnow()
            DBSession.add(user_david)
        assert DBSession.query(User).filter(User.admin_at.isnot(None)).count() == 2

        resp = app.post("/admins/", {"user_pk": user_david.pk}, user=user_david)

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/admins/"

        resp = resp.follow()

        assert (
            "Vous ne pouvez pas vous retirer du statut d’administrateur." in resp.text
        )
        assert DBSession.query(User).filter(User.admin_at.isnot(None)).count() == 2
