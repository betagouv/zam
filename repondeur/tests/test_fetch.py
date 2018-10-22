from pathlib import Path
import transaction

import pytest
import responses


class TestGetPossibleUrls:
    def test_assemblee_nationale(self):
        from zam_repondeur.fetch import get_possible_texte_urls
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="an",
            session="15",
            num_texte=269,
            titre="Titre lecture",
            organe="PO420120",
        )
        assert get_possible_texte_urls(lecture) == [
            "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
            "http://www.assemblee-nationale.fr/15/ta-commission/r0269-a0.asp",
        ]

    def test_senat(self):
        from zam_repondeur.fetch import get_possible_texte_urls
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="senat",
            session="2017-2018",
            num_texte=63,
            titre="Titre lecture",
            organe="PO78718",
        )
        assert get_possible_texte_urls(lecture) == [
            "https://www.senat.fr/leg/pjl17-063.html"
        ]


class TestGetArticlesAN:
    @responses.activate
    def test_new_articles_are_created(self, app, lecture_an, amendements_an):
        from zam_repondeur.fetch import get_articles
        from zam_repondeur.models import DBSession

        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
            body=(Path(__file__).parent / "sample_data" / "pl0269.html").read_text(
                "utf-8", "ignore"
            ),
            status=200,
        )

        DBSession.add(lecture_an)

        # We only have the article mentioned by the amendement
        assert {article.num for article in lecture_an.articles} == {"1"}

        changed = get_articles(lecture_an)

        assert changed

        # We now also have article 2 after scraping the web page
        assert {article.num for article in lecture_an.articles} == {"1", "2"}

    @responses.activate
    def test_article_ranges(self, app, lecture_an):
        from zam_repondeur.fetch import get_articles
        from zam_repondeur.models import DBSession

        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
            body=(Path(__file__).parent / "sample_data" / "pl0387.html")
            .read_text("latin-1")
            .encode("latin-1"),
            status=200,
        )

        DBSession.add(lecture_an)

        # No articles initially
        assert {article.num for article in lecture_an.articles} == set()

        changed = get_articles(lecture_an)

        assert changed

        nums = {article.num for article in lecture_an.articles}

        # "Articles 1er et 2"
        assert {"1", "2"}.issubset(nums)

        # "Articles 19 à 24"
        assert {"19", "20", "21", "22", "23", "24"}.issubset(nums)

    @responses.activate
    def test_existing_articles_are_updated(self, app, lecture_an, amendements_an):
        from zam_repondeur.fetch import get_articles
        from zam_repondeur.models import DBSession, Amendement

        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
            body=(Path(__file__).parent / "sample_data" / "pl0269.html").read_text(
                "utf-8", "ignore"
            ),
            status=200,
        )

        DBSession.add(lecture_an)

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.article.titre == ""
        assert amendement.article.contenu == {}

        changed = get_articles(lecture_an)

        assert changed

        # We can get the article contents from an amendement
        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.article.titre == "Dispositions relatives l'exercice 2016"
        assert amendement.article.contenu["001"].startswith(
            "Au titre de l'exercice 2016"
        )

    @responses.activate
    def test_custom_article_titles_are_preserved(self, app, lecture_an, amendements_an):
        from zam_repondeur.fetch import get_articles
        from zam_repondeur.models import DBSession, Amendement

        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
            body=(Path(__file__).parent / "sample_data" / "pl0269.html").read_text(
                "utf-8", "ignore"
            ),
            status=200,
        )

        DBSession.add(lecture_an)

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.article.titre == ""
        assert amendement.article.contenu == {}

        # Let's set a custom article title
        amendement.article.titre = "My custom title"

        changed = get_articles(lecture_an)

        assert changed

        # We can get the article contents from an amendement
        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.article.titre == "My custom title"
        assert amendement.article.contenu["001"].startswith(
            "Au titre de l'exercice 2016"
        )

    @responses.activate
    def test_intersticial_articles_are_not_updated(self, app, lecture_an):
        from zam_repondeur.fetch import get_articles
        from zam_repondeur.models import DBSession, Article

        article_avant_2 = Article.create(
            lecture=lecture_an, type="article", num="2", pos="avant"
        )
        DBSession.add(article_avant_2)

        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
            body=(Path(__file__).parent / "sample_data" / "pl0269.html").read_text(
                "utf-8", "ignore"
            ),
            status=200,
        )

        changed = get_articles(lecture_an)

        assert changed

        article = DBSession.query(Article).filter(Article.pos == "avant").first()
        assert article.titre == ""
        assert article.contenu == {}

    @responses.activate
    def test_fallback_to_alternative_url_pattern(self, app, lecture_an, amendements_an):
        from zam_repondeur.fetch import get_articles
        from zam_repondeur.models import DBSession, Amendement

        with transaction.manager:
            lecture_an.num_texte = 575
            lecture_an.organe = "PO717460"
            lecture_an.titre = "Première lecture – Séance publique"

            amendements_an[0].article.num = "2"

            # The objects are no longer bound to a session here, as they were created in
            # a previous transaction, so we add them to the current session to make sure
            # that our changes will be committed with the current transaction
            DBSession.add(lecture_an)
            DBSession.add_all(amendements_an)

        # This URL pattern will fail
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/projets/pl0575.asp",
            status=404,
        )

        # So we want to use this one instead
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/ta-commission/r0575-a0.asp",
            body=(Path(__file__).parent / "sample_data" / "r0575-a0.html").read_text(
                "utf-8", "ignore"
            ),
            status=200,
        )

        changed = get_articles(lecture_an)

        assert changed

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.article.contenu["001"].startswith(
            "Le code des relations entre"
        )

    @responses.activate
    def test_not_found(self, app, lecture_an, amendements_an):
        from zam_repondeur.fetch import get_articles
        from zam_repondeur.models import DBSession, Amendement

        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
            status=404,
        )
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/ta-commission/r0269-a0.asp",
            status=404,
        )

        changed = get_articles(lecture_an)

        assert not changed

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.article.contenu == {}


class TestGetArticlesSenat:
    @responses.activate
    def test_get_articles_senat(
        self, app, lecture_senat, amendements_senat, article1_an
    ):
        from zam_repondeur.fetch import get_articles
        from zam_repondeur.models import DBSession, Amendement, Article

        responses.add(
            responses.GET,
            "https://www.senat.fr/leg/pjl17-063.html",
            body=(Path(__file__).parent / "sample_data" / "pjl17-063.html").read_text(
                "utf-8", "ignore"
            ),
            status=200,
        )

        changed = get_articles(lecture_senat)

        assert changed

        amendement = DBSession.query(Amendement).filter(Amendement.num == 6666).first()
        assert amendement.article.contenu["001"].startswith(
            "Au titre de l'exercice 2016"
        )

        # We should not modify articles from unrelated lectures
        article = DBSession.query(Article).filter_by(pk=article1_an.pk).one()
        assert article is not amendement.article
        assert article.contenu == {}

    @responses.activate
    def test_get_articles_senat_with_mult(self, app, lecture_senat, amendements_senat):
        from zam_repondeur.fetch import get_articles
        from zam_repondeur.models import DBSession, Amendement

        responses.add(
            responses.GET,
            "https://www.senat.fr/leg/pjl17-063.html",
            body=(Path(__file__).parent / "sample_data" / "pjl17-063.html").read_text(
                "utf-8", "ignore"
            ),
            status=200,
        )

        with transaction.manager:
            amendement = amendements_senat[0]
            amendement.article.num = "4"
            amendement.article.mult = "bis"

            # The objects are no longer bound to a session here, as they were created in
            # a previous transaction, so we add them to the current session to make sure
            # that our changes will be committed with the current transaction
            DBSession.add(amendement)

        changed = get_articles(lecture_senat)

        assert changed

        amendement = DBSession.query(Amendement).filter(Amendement.num == 6666).first()
        assert amendement.article.contenu["001"].startswith("Ne donnent pas lieu à")


def test_get_section_title():
    from zam_repondeur.fetch import get_section_title

    items = [
        {
            "id": "P1",
            "titre": "Dispositions relatives à l'exercice 2016",
            "type": "section",
            "type_section": "partie",
        },
        {
            "alineas": {},
            "order": 1,
            "section": "P1",
            "statut": "none",
            "titre": "1er",
            "type": "article",
        },
    ]
    article = {
        "alineas": {},
        "order": 1,
        "section": "P1",
        "statut": "none",
        "titre": "1er",
        "type": "article",
    }
    title = get_section_title(items, article)
    assert title == "Dispositions relatives à l'exercice 2016"


def test_get_section_title_unknown_reference():
    from zam_repondeur.fetch import get_section_title

    items = [
        {
            "id": "P1",
            "titre": "Dispositions relatives à l'exercice 2016",
            "type": "section",
            "type_section": "partie",
        },
        {
            "alineas": {},
            "order": 1,
            "section": "P1",
            "statut": "none",
            "titre": "1er",
            "type": "article",
        },
    ]
    article = {
        "alineas": {},
        "order": 1,
        "section": "FOO",
        "statut": "none",
        "titre": "1er",
        "type": "article",
    }
    assert get_section_title(items, article) == ""


@pytest.mark.parametrize(
    "input,num,mult",
    [
        ("liminaire", "0", ""),
        ("1er", "1", ""),
        ("2", "2", ""),
        ("3 bis", "3", "bis"),
        ("5 ter AAA", "5", "ter AAA"),
    ],
)
def test_get_article_num_mult(input, num, mult):
    from zam_repondeur.fetch import get_article_num_mult

    assert get_article_num_mult(input) == (num, mult)


@pytest.mark.parametrize(
    "input,output",
    [
        ("liminaire", [("0", "")]),
        ("1er", [("1", "")]),
        ("2", [("2", "")]),
        ("3 bis", [("3", "bis")]),
        ("5 ter AAA", [("5", "ter AAA")]),
        ("19 à 21", [("19", ""), ("20", ""), ("21", "")]),
        ("34 bis A à 34 bis C", [("34", "bis A"), ("34", "bis B"), ("34", "bis C")]),
        ("34 bis B à 34 bis D", [("34", "bis B"), ("34", "bis C"), ("34", "bis D")]),
    ],
)
def test_get_article_nums_mults(input, output):
    from zam_repondeur.fetch import get_article_nums_mults

    assert get_article_nums_mults({"titre": input}) == output
