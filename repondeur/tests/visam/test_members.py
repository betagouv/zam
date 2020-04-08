import pytest
import transaction


class TestMembersMenuAction:
    def test_admin_sees_link_to_manage_members_in_menu(self, app, user_admin):
        resp = app.get("/conseils/", user=user_admin)
        menu_actions = [
            elem.text().strip() for elem in resp.parser.css(".menu-actions > li > a")
        ]
        assert "Gestion des membres" in menu_actions


class TestMembersList:
    @pytest.mark.usefixtures("user_david")
    def test_only_accessible_to_admin(self, app, user_admin):
        resp = app.get("/members/", user=user_admin)

        assert resp.status_code == 200
        assert resp.content_type == "text/html"

        trs = resp.parser.css("tbody tr")
        assert len(trs) == 2
        assert "David (david@exemple.gouv.fr)" in trs[0].text()
        assert "Admin user (user@admin.gouv.fr)" in trs[1].text()

    def test_not_accessible_to_regular_user(self, app, user_david):
        resp = app.get("/members/", user=user_david)

        assert resp.status_code == 302
        assert resp.location == "https://visam.test/"


class TestMembersAdd:
    def test_create(self, app, user_admin, user_david):
        from zam_repondeur.models import Chambre, DBSession, User

        DBSession.add(user_david)
        assert user_david.chambres == []

        resp = app.post(
            "/members/add",
            {"user_pk": user_david.pk, "chambre_name": str(Chambre.CCFP)},
            user=user_admin,
        )

        assert resp.status_code == 302
        assert resp.location == "https://visam.test/members/"

        resp = resp.follow()

        assert resp.status_code == 200
        assert resp.content_type == "text/html"
        assert (
            "Membre David (david@exemple.gouv.fr) ajouté au "
            "Conseil commun de la fonction publique avec succès."
        ) in resp.text

        with transaction.manager:
            DBSession.add(user_admin)
            assert len(user_admin.events) == 1
            assert user_admin.events[0].render_summary() == (
                "<abbr title='user@admin.gouv.fr'>Admin user</abbr> a ajouté "
                "David (david@exemple.gouv.fr) au "
                "Conseil commun de la fonction publique."
            )

        user_david = DBSession.query(User).filter_by(pk=user_david.pk).one()  # Refresh.
        assert user_david.chambres == [Chambre.CCFP]

    def test_not_possible_to_regular_user(self, app, user_david):
        from zam_repondeur.models import Chambre, DBSession, User

        DBSession.add(user_david)
        assert user_david.chambres == []

        resp = app.post(
            "/members/add",
            {"user_pk": user_david.pk, "chambre_name": str(Chambre.CCFP)},
            user=user_david,
        )

        assert resp.status_code == 302
        assert resp.location == "https://visam.test/"

        user_david = DBSession.query(User).filter_by(pk=user_david.pk).one()  # Refresh.
        assert user_david.chambres == []


class TestMembersDelete:
    def test_delete(self, app, user_admin, user_ccfp):
        from zam_repondeur.models import Chambre, DBSession, User

        DBSession.add(user_ccfp)
        assert user_ccfp.chambres == [Chambre.CCFP]

        resp = app.post(
            "/members/",
            {"user_pk": user_ccfp.pk, "chambre_name": str(Chambre.CCFP)},
            user=user_admin,
        )

        assert resp.status_code == 302
        assert resp.location == "https://visam.test/members/"

        resp = resp.follow()

        assert resp.status_code == 200
        assert resp.content_type == "text/html"

        assert (
            "Membre David (david@exemple.gouv.fr) retiré du "
            "Conseil commun de la fonction publique avec succès."
        ) in resp.text

        with transaction.manager:
            DBSession.add(user_admin)
            assert len(user_admin.events) == 1
            assert user_admin.events[0].render_summary() == (
                "<abbr title='user@admin.gouv.fr'>Admin user</abbr> a retiré "
                "David (david@exemple.gouv.fr) du "
                "Conseil commun de la fonction publique."
            )

        user_ccfp = DBSession.query(User).filter_by(pk=user_ccfp.pk).one()  # Refresh.
        assert user_ccfp.chambres == []

    def test_not_possible_to_regular_user(self, app, user_david, user_ccfp):
        from zam_repondeur.models import Chambre, DBSession, User

        DBSession.add(user_ccfp)
        assert user_ccfp.chambres == [Chambre.CCFP]

        resp = app.post(
            "/members/",
            {"user_pk": user_ccfp.pk, "chambre_name": str(Chambre.CCFP)},
            user=user_david,
        )

        assert resp.status_code == 302
        assert resp.location == "https://visam.test/"

        user_ccfp = DBSession.query(User).filter_by(pk=user_ccfp.pk).one()  # Refresh.
        assert user_ccfp.chambres == [Chambre.CCFP]
