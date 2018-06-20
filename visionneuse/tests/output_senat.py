def test_has_title(output):
    assert (
        output.css_first("h1").text() == "Financement de la sécurité sociale pour 2018"
    )


def test_number_reponses(output):
    assert len(output.tags("article")) == 306


def test_nature_reponses(output):
    assert len(output.css("header.reponse.positive")) == 30
    assert len(output.css("header.reponse.negative")) == 267


def test_articles_presence(output):
    articles = output.tags("section")
    assert len(articles) == 72
    assert articles[0].css_first("h2").text().strip() == "Article 3"


def test_articles_links_presence(output):
    article = output.tags("section")[0]
    links = article.css("header .wrapper a")
    assert len(links) == 2
    assert links[0].text().strip() == "Jaune"
    assert links[1].text().strip() == "Texte"


def test_articles_jaune_presence(output):
    article = output.tags("section")[0]
    jaune = article.css_first(".is-hidden .jaune")
    assert jaune.text().strip().startswith("Rectification des dotations des branches")


def test_articles_texte_presence(output):
    article = output.tags("section")[0]
    texte = article.css_first(".is-hidden .article")
    assert texte.text().strip().startswith("001")


def test_reponse_unique_amendement(output):
    reponse = output.tags("article")[1]
    assert "443" in reponse.css_first("h2").text()
    assert len(reponse.css("header p.authors .author")) == 1


def test_reponse_has_content(output):
    reponse = output.tags("article")[0]
    assert reponse.css_first("header .button").text().strip().startswith("Réponse\xa0:")
    assert (
        reponse.css_first(".reponse-detail").text().strip().startswith("Rédactionnel")
    )


def test_reponse_multiple_amendement(output):
    reponse = output.tags("article")[0]
    assert "31," in reponse.css_first("h2").text()
    assert "146 et" in reponse.css_first("h2").text()
    assert len(reponse.css("header p.authors .author")) == 4


def test_reponse_has_amendements(output):
    reponse = output.tags("article")[0]
    details_titles = reponse.css(".amendement-detail h3")
    details_contents = reponse.css(".amendement-detail div")
    assert len(details_titles) == 65
    assert details_titles[0].text().strip().startswith("Amendement 31")
    assert (
        details_contents[0]
        .text()
        .strip()
        .startswith("Cet amendement précise l’assiette")
    )


def test_menu_templates_presence(output):
    assert len(output.tags("template")) == 1


def test_menu_template_content(output):
    menu = output.tags("template")[0]
    assert len(menu.css("a")) == 72
