import pytest


class TestLectureMenuActions:
    @pytest.fixture
    def menu_actions(self, app, lecture_an, user_david):
        resp = app.get(
            "/dossiers/plfss-2018/lectures/an.15.269.PO717460/amendements/",
            user=user_david,
        )
        return [
            elem.text().strip() for elem in resp.parser.css(".menu-actions > li > a")
        ]

    def test_user_can_see_dossier_de_banc(self, menu_actions):
        assert "Dossier de banc" in menu_actions

    def test_user_can_see_options_avancees(self, menu_actions):
        assert "Options avancées" in menu_actions
