class TestListArticles:
    def test_articles_are_sorted(self, app, article1_an, article1av_an):
        resp = app.get("http://localhost/lectures/an.15.269.PO717460/articles/")
        assert resp.status_code == 200
        titles = [node.text().strip() for node in resp.parser.css(".article")]
        assert titles == ["Article add. av. 1", "Article 1"]

    def test_uppercase_roman_numbers_are_preserved(self, app, chapitre_1er_an):
        resp = app.get("http://localhost/lectures/an.15.269.PO717460/articles/")
        assert resp.status_code == 200
        titles = [node.text().strip() for node in resp.parser.css(".article")]
        assert titles == ["Chapitre Ier"]
