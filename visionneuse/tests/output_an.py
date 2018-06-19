def test_has_title(output):
    assert output.css_first("h1").text() == "PLFSS pour 2018"


def test_number_reponses(output):
    assert len(output.tags("article")) == 149


def test_nature_reponses(output):
    assert len(output.css("header.reponse.positive")) == 53
    assert len(output.css("header.reponse.negative")) == 96


def test_articles_presence(output):
    articles = output.tags("section")
    assert len(articles) == 40
    assert articles[0].css_first("h2").text().strip() == "Article 7"


def test_articles_links_presence(output):
    article = output.tags("section")[0]
    links = article.css("header .wrapper a")
    assert len(links) == 2
    assert links[0].text().strip() == "Jaune"
    assert links[1].text().strip() == "Texte"


def test_articles_jaune_presence(output):
    article = output.tags("section")[0]
    jaune = article.css_first(".is-hidden .jaune")
    assert jaune.text().strip().startswith("Mesures de pouvoir d’achat")


def test_articles_texte_presence(output):
    article = output.tags("section")[0]
    texte = article.css_first(".is-hidden .article")
    assert texte.text().strip().startswith("001")


def test_reponse_unique_amendement(output):
    reponse = output.tags("article")[2]
    assert "357" in reponse.css_first("h2").text()
    assert len(reponse.css("header p.authors .author")) == 1


def test_reponse_multiple_amendement(output):
    reponse = output.tags("article")[1]
    assert "56 et" in reponse.css_first("h2").text()
    assert "69" in reponse.css_first("h2").text()
    assert len(reponse.css("header p.authors .author")) == 2


def test_reponse_has_content(output):
    reponse = output.tags("article")[0]
    assert reponse.css_first("header .button").text().strip().startswith("Réponse\xa0:")
    assert (
        reponse.css_first(".reponse-detail").text().strip().startswith("Suppression de")
    )


def test_reponse_has_amendements(output):
    reponse = output.tags("article")[0]
    details_titles = reponse.css(".amendement-detail h3")
    details_contents = reponse.css(".amendement-detail div")
    assert len(details_titles) == 7
    assert details_titles[0].text().strip().startswith("Amendement 5")
    assert (
        details_contents[1]
        .text()
        .strip()
        .startswith("L’article\xa07 du PLFSS vise à augmenter")
    )


def test_menu_templates_presence(output):
    assert len(output.tags("template")) == 1


def test_menu_template_content(output):
    menu = output.tags("template")[0]
    assert len(menu.css("a")) == 40
