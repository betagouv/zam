import transaction


class TestListArticles:
    def test_articles_are_sorted(self, app, article1_an, article1av_an, amendements_an):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            amendements_an[0].article = article1av_an
            amendements_an[0].user_content.avis = "Favorable"
            DBSession.add_all(amendements_an)

        resp = app.get(
            "/lectures/an.15.269.PO717460/articles/", user="user@example.com"
        )
        assert resp.status_code == 200
        titles = [node.text().strip() for node in resp.parser.css(".article")]
        assert titles == ["Article add. av. 1", "Article 1"]

    def test_additional_articles_without_avis_are_not_listed(
        self, app, article1_an, article1av_an, amendements_an
    ):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            amendements_an[0].article = article1av_an
            DBSession.add_all(amendements_an)

        resp = app.get(
            "/lectures/an.15.269.PO717460/articles/", user="user@example.com"
        )
        assert resp.status_code == 200
        titles = [node.text().strip() for node in resp.parser.css(".article")]
        assert titles == ["Article 1"]

    def test_uppercase_roman_numbers_are_preserved(self, app, chapitre_1er_an):
        resp = app.get(
            "/lectures/an.15.269.PO717460/articles/", user="user@example.com"
        )
        assert resp.status_code == 200
        titles = [node.text().strip() for node in resp.parser.css(".article")]
        assert titles == ["Chapitre Ier"]

    def test_link_to_articles_list(self, app, lecture_an):
        resp = app.get(
            "/lectures/an.15.269.PO717460/articles/", user="user@example.com"
        )
        assert resp.status_code == 200
        link = resp.parser.css_first("nav.main .list").attributes.get("href")
        assert link == "https://zam.test/lectures/an.15.269.PO717460/articles/"
