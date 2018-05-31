def test_has_title(output):
    assert output.css_first("h1").text().startswith("Projet Loi de")


def test_number_reponses(output):
    assert len(output.tags("article")) == 210


def test_nature_reponses(output):
    assert len(output.css("header.reponse.positive")) == 28
    assert len(output.css("header.reponse.negative")) == 151


def test_reponse_unique_amendement(output):
    reponse = output.tags("article")[1]
    assert "443" in reponse.css_first("h2").text()
    assert len(reponse.css("header p.authors strong")) == 1


def test_reponse_has_content(output):
    reponse = output.tags("article")[0]
    assert reponse.css_first("div details summary").text().strip()
    assert reponse.css_first("div details div.reponse").text().strip()


def test_reponse_multiple_amendement(output):
    reponse = output.tags("article")[0]
    assert "31," in reponse.css_first("h2").text()
    assert "146 et" in reponse.css_first("h2").text()
    assert len(reponse.css("header p.authors strong")) == 4


def test_reponse_has_amendements(output):
    reponse = output.tags("article")[0]
    details = reponse.css("details")
    assert len(details) == 66
    assert (
        details[1]
        .css_first("summary")
        .text()
        .strip()
        .startswith("Amendement 31")
    )
    assert (
        details[1]
        .css_first("div")
        .text()
        .strip()
        .startswith("Cet amendement précise l’assiette")
    )


def test_reponse_has_article_hook(output):
    reponse = output.tags("article")[0]
    assert reponse.css_first('[data-article="article-3"]')


def test_article_templates_presence(output):
    assert len(output.tags("template")) == 56


def test_article_template_content(output):
    article = output.tags("template")[0]
    assert len(article.css("details")) == 2


def test_article_template_has_jaune(output):
    article = output.tags("template")[0]
    jaune = article.css("details")[1]
    assert jaune.css_first("summary").text() == "Article 10\xa0: jaune"
    assert jaune.css_first("div.jaune").text().strip()
