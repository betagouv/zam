from zam_visionneuse.models import (
    Amendement,
    Amendements,
    Article,
    Articles,
    Reponse,
    Reponses,
)


def test_article_pk_from_raw():
    assert Article.pk_from_raw({"document": "foo.pdf"}) == "foo"


def test_amendement_pk_from_raw():
    assert Amendement.pk_from_raw({"document": "foo-xx.pdf"}) == "foo"


def test_reponse_pk_from_raw():
    assert Reponse.pk_from_raw({"presentation": "foo", "idReponse": 1}) == "Zm9v"


def test_articles_load():
    items = [
        {
            "id": 1,
            "pk": "article-1",
            "etat": "",
            "multiplicatif": "",
            "titre": "Approbation des tableaux d'\u00e9quilibre",
            "document": "article-1.pdf",
            "amendements": [],
        }
    ]
    articles = Articles.load(items)
    assert list(articles.keys()) == ["article-1"]
    article = list(articles.values())[0]
    assert article.pk == "article-1"
    assert article.id == 1
    assert article.titre == "Approbation des tableaux d'équilibre"
    assert article.etat == ""
    assert article.multiplicatif == ""
    assert article.jaune == ""
    assert article.content == "TODO"
    assert article.amendements == []


def test_article_slug():
    items = [
        {
            "id": 1,
            "pk": "article-1",
            "etat": "",
            "multiplicatif": "",
            "titre": "Approbation des tableaux d'\u00e9quilibre",
            "document": "article-1.pdf",
            "amendements": [],
        }
    ]
    articles = Articles.load(items)
    article = list(articles.values())[0]
    assert article.slug == "article-1"
    items = [
        {
            "id": 1,
            "pk": "article-1",
            "etat": "ap",
            "multiplicatif": "bis",
            "titre": "Approbation des tableaux d'\u00e9quilibre",
            "document": "article-1.pdf",
            "amendements": [],
        }
    ]
    articles = Articles.load(items)
    article = list(articles.values())[0]
    assert article.slug == "article-1-ap-bis"


def test_amendements_load():
    items = [
        {
            "id": 1,
            "pk": "article-1",
            "etat": "",
            "multiplicatif": "",
            "titre": "Approbation des tableaux d'\u00e9quilibre",
            "document": "article-1.pdf",
            "amendements": [
                {
                    "id": 5,
                    "pk": "000005",
                    "etat": "",
                    "gouvernemental": False,
                    "groupe": {
                        "libelle": "Les D\u00e9veloppeurs",
                        "couleur": "#133700",
                    },
                    "auteur": "M.\u00a0David",
                    "document": "000005-00.pdf",
                    "objet": "<p>Amendement de précision.</p>",
                    "dispositif": "<p>Alinéa 8</p>",
                }
            ],
        }
    ]
    articles = Articles.load(items)
    amendements = Amendements.load(items, articles)
    assert list(amendements.keys()) == ["000005"]
    amendement = list(amendements.values())[0]
    assert amendement.pk == "000005"
    assert amendement.id == 5
    assert amendement.article.id == 1
    assert amendement.article.amendements == [amendement]
    assert amendement.auteur == "M.\xa0David"
    assert amendement.groupe == {"libelle": "Les Développeurs", "couleur": "#133700"}
    assert amendement.objet == "<p>Amendement de précision.</p>"
    assert amendement.dispositif == "<p>Alinéa 8</p>"
    assert amendement.document == "000005-00.pdf"
    assert amendement.gouvernemental is False


def test_reponses_load():
    aspirateur_data = [
        {
            "id": 1,
            "pk": "article-1",
            "etat": "",
            "multiplicatif": "",
            "titre": "Approbation des tableaux d'\u00e9quilibre",
            "document": "article-1.pdf",
            "amendements": [
                {
                    "id": 5,
                    "pk": "000005",
                    "etat": "",
                    "gouvernemental": False,
                    "groupe": {
                        "libelle": "Les D\u00e9veloppeurs",
                        "couleur": "#133700",
                    },
                    "auteur": "M.\u00a0David",
                    "document": "000005-00.pdf",
                    "objet": "<p>Amendement de précision.</p>",
                    "dispositif": "<p>Alinéa 8</p>",
                }
            ],
        }
    ]
    drupal_data = [
        {
            "idArticle": 1,
            "etat": "",
            "multiplicatif": "",
            "titre": "Approbation des tableaux d'\u00e9quilibre",
            "document": "article-1.pdf",
            "amendements": [
                {
                    "idAmendement": 5,
                    "etat": "",
                    "gouvernemental": False,
                    "groupe": {
                        "libelle": "Les D\u00e9veloppeurs",
                        "couleur": "#133700",
                    },
                    "auteurs": [{"auteur": "M.\u00a0David", "couleur": "#ffffff"}],
                    "reponse": {
                        "idReponse": 12,
                        "avis": "D\u00e9favorable",
                        "presentation": "<p><strong>Suppression de l\u2019article</strong></p>",
                        "reponse": "<p>Cet article met en \u0153uvre...</p>",
                    },
                    "document": "000005-00.pdf",
                    "objet": "<p>Amendement de précision.</p>",
                    "dispositif": "<p>Alinéa 8</p>",
                }
            ],
        }
    ]
    articles = Articles.load(aspirateur_data)
    amendements = Amendements.load(aspirateur_data, articles)
    reponses = Reponses.load(drupal_data, articles, amendements)
    assert list(reponses.keys())[0].startswith("PHA+PHN0cm9uZz5TdXBwcmV")
    reponse = list(reponses.values())[0]
    assert reponse.pk.startswith("PHA+PHN0cm9uZz5TdXBwcmV")
    assert reponse.presentation == "<p><strong>Suppression de l’article</strong></p>"
    assert reponse.content == "<p>Cet article met en œuvre...</p>"
    assert reponse.avis == "Défavorable"
