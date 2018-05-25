from models import (
    Amendement, Amendements, Article, Articles, Reponse, Reponses
)


def test_article_pk_from_raw():
    assert Article.pk_from_raw({'document': 'foo.pdf'}) == 'foo'


def test_amendement_pk_from_raw():
    assert Amendement.pk_from_raw({'document': 'foo.pdf'}) == 'foo'


def test_reponse_pk_from_raw():
    assert Reponse.pk_from_raw({'presentation': 'foo'}) == 'Zm9v'


def test_articles_load():
    items = [{
        "idArticle": 1,
        "etat": "",
        "multiplicatif": "",
        "titre": "Approbation des tableaux d'\u00e9quilibre",
        "document": "article-1.pdf"
    }]
    articles = Articles.load(items, None)
    assert list(articles.keys()) == ['article-1']
    article = list(articles.values())[0]
    assert article.pk == 'article-1'
    assert article.id == 1
    assert article.title == "Approbation des tableaux d'équilibre"
    assert article.state == ''
    assert article.multiplier == ''
    assert article.jaune == ''
    assert article.content == 'TODO'
    assert article.amendements == []


def test_amendements_load():
    items = [{
        "idArticle": 1,
        "etat": "",
        "multiplicatif": "",
        "titre": "Approbation des tableaux d'\u00e9quilibre",
        "document": "article-1.pdf",
        "amendements": [{
            "idAmendement": 5,
            "etat": "",
            "gouvernemental": False,
            "groupesParlementaires": [
                {
                    "libelle": "Les D\u00e9veloppeurs",
                    "couleur": "#133700"
                }
            ],
            "auteurs": [
                {
                    "auteur": "M.\u00a0David",
                    "couleur": "#ffffff"
                }
            ],
            "document": "000005-00.pdf"
        }]
    }]
    articles = Articles.load(items, None)
    amendements = Amendements.load(items, articles, None)
    assert list(amendements.keys()) == ['000005-00']
    amendement = list(amendements.values())[0]
    assert amendement.pk == '000005-00'
    assert amendement.id == 5
    assert amendement.article.id == 1
    assert amendement.article.amendements == [amendement]
    assert amendement.authors == 'M.\xa0David'
    assert amendement.group == {
        'label': 'Les Développeurs',
        'color': '#133700'
    }
    assert amendement.content == ''
    assert amendement.summary == ''
    assert amendement.document == '000005-00.pdf'
    assert amendement.is_gouvernemental is False


def test_reponses_load():
    items = [{
        "idArticle": 1,
        "etat": "",
        "multiplicatif": "",
        "titre": "Approbation des tableaux d'\u00e9quilibre",
        "document": "article-1.pdf",
        "amendements": [{
            "idAmendement": 5,
            "etat": "",
            "gouvernemental": False,
            "groupesParlementaires": [
                {
                    "libelle": "Les D\u00e9veloppeurs",
                    "couleur": "#133700"
                }
            ],
            "auteurs": [
                {
                    "auteur": "M.\u00a0David",
                    "couleur": "#ffffff"
                }
            ],
            "reponse": {
                "idReponse": 12,
                "avis": "D\u00e9favorable",
                "presentation":
                    "<p><strong>Suppression de l\u2019article</strong></p>",
                "reponse": "<p>Cet article met en \u0153uvre...</p>"
            },
            "document": "000005-00.pdf"
        }]
    }]
    articles = Articles.load(items, None)
    amendements = Amendements.load(items, articles, None)
    reponses = Reponses.load(items, articles, amendements, None)
    assert list(reponses.keys())[0].startswith('PHA+PHN0cm9uZz5TdXBwcmV')
    reponse = list(reponses.values())[0]
    assert reponse.pk.startswith('PHA+PHN0cm9uZz5TdXBwcmV')
    assert (reponse.presentation ==
            '<p><strong>Suppression de l’article</strong></p>')
    assert reponse.content == '<p>Cet article met en œuvre...</p>'
    assert reponse.avis == 'Défavorable'
