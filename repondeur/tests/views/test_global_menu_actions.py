import pytest


class TestUserMenuActions:
    @pytest.fixture
    def menu_actions(self, app, user_david):
        resp = app.get("/dossiers/", user=user_david)
        return [
            elem.text().strip() for elem in resp.parser.css(".menu-actions > li > a")
        ]

    def test_user_can_edit_profile(self, menu_actions):
        assert "David" in menu_actions

    def test_user_can_logout(self, menu_actions):
        assert "Déconnexion" in menu_actions


class TestAdminMenuActions:
    @pytest.fixture
    def menu_actions(self, app, user_sgg):
        resp = app.get("/dossiers/", user=user_sgg)
        return [
            elem.text().strip() for elem in resp.parser.css(".menu-actions > li > a")
        ]

    def test_admin_can_manage_whitelist(self, menu_actions):
        assert "Gestion des accès" in menu_actions

    def test_admin_can_manage_admins(self, menu_actions):
        assert "Gestion des administrateur·ice·s" in menu_actions
