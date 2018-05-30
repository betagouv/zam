def test_has_title(document):
    assert document.css_first("h1").text().startswith("Projet Loi de")


def test_number_reponses(document):
    assert len(document.tags("article")) == 316


def test_nature_reponses(document):
    assert len(document.css("header.reponse.positive")) == 30
    assert len(document.css("header.reponse.negative")) == 249


def test_reponse_unique_amendement(document):
    reponse = document.tags("article")[1]
    assert "443" in reponse.css_first("h2").text()
    assert len(reponse.css("header p.authors strong")) == 1


def test_reponse_has_content(document):
    reponse = document.tags("article")[0]
    assert reponse.css_first("div details summary").text().strip()
    assert reponse.css_first("div details div.reponse").text().strip()


def test_reponse_multiple_amendement(document):
    reponse = document.tags("article")[0]
    assert "31," in reponse.css_first("h2").text()
    assert "146 et" in reponse.css_first("h2").text()
    assert len(reponse.css("header p.authors strong")) == 4


def test_reponse_has_amendements(document):
    reponse = document.tags("article")[0]
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


def test_reponse_has_article_hook(document):
    reponse = document.tags("article")[0]
    assert reponse.css_first('[data-article="article-3"]')


def test_article_templates_presence(document):
    assert len(document.tags("template")) == 113


def test_article_template_content(document):
    article = document.tags("template")[0]
    assert len(article.css("details")) == 2


def test_article_template_has_jaune(document):
    article = document.tags("template")[0]
    jaune = article.css("details")[1]
    assert jaune.css_first("summary").text() == "Article 1\xa0: jaune"
    assert jaune.css_first("div.jaune").text().strip()
