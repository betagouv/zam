def test_has_title(output):
    assert output.css_first("h1").text() == "PLFSS pour 2018"


def test_number_reponses(output):
    assert len(output.tags("article")) == 149


def test_nature_reponses(output):
    assert len(output.css("header.reponse.positive")) == 53
    assert len(output.css("header.reponse.negative")) == 87


def test_reponse_unique_amendement(output):
    reponse = output.tags("article")[2]
    assert "357" in reponse.css_first("h2").text()
    assert len(reponse.css("header p.authors strong")) == 1


def test_reponse_multiple_amendement(output):
    reponse = output.tags("article")[1]
    assert "56 et" in reponse.css_first("h2").text()
    assert "69" in reponse.css_first("h2").text()
    assert len(reponse.css("header p.authors strong")) == 2


def test_reponse_has_content(output):
    reponse = output.tags("article")[0]
    assert reponse.css_first("div details summary").text().strip()
    assert reponse.css_first("div details div.reponse").text().strip()


def test_reponse_has_amendements(output):
    reponse = output.tags("article")[0]
    details = reponse.css("details")
    assert len(details) == 8
    assert details[1].css_first("summary").text().strip().startswith("Amendement 5")
    assert (
        details[1]
        .css_first("div")
        .text()
        .strip()
        .startswith("L’article\xa07 du PLFSS vise à augmenter")
    )


def test_reponse_has_article_hook(output):
    reponse = output.tags("article")[0]
    assert reponse.css_first('[data-article="article-7"]')


def test_article_templates_presence(output):
    assert len(output.tags("template")) == 44


def test_article_template_content(output):
    article = output.tags("template")[1]
    assert len(article.css("details")) == 2


def test_article_template_has_jaune(output):
    article = output.tags("template")[1]
    jaune = article.css("details")[1]
    assert jaune.css_first("summary").text() == "Article 11\xa0: jaune"
    assert jaune.css_first("div.jaune").text().strip()
