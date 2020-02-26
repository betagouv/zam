from datetime import date
from pathlib import Path

import pytest
import responses
import transaction

SAMPLE_DATA_DIR = Path(__file__).parent.parent / "sample_data"


class TestGetPossibleUrls:
    def test_assemblee_nationale_pjl(self, texte_plfss2018_an_premiere_lecture):
        from zam_repondeur.services.fetch.articles import get_possible_texte_urls

        assert get_possible_texte_urls(texte_plfss2018_an_premiere_lecture) == [
            "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
            "http://www.assemblee-nationale.fr/15/ta-commission/r0269-a0.asp",
        ]

    def test_assemblee_nationale_ppl(self, db):
        from zam_repondeur.services.fetch.articles import get_possible_texte_urls
        from zam_repondeur.models import Chambre, Texte, TypeTexte

        with transaction.manager:
            texte = Texte.create(
                type_=TypeTexte.PROPOSITION,
                chambre=Chambre.AN,
                legislature=15,
                numero=269,
                date_depot=date(2017, 10, 11),
            )

        assert get_possible_texte_urls(texte) == [
            "http://www.assemblee-nationale.fr/15/propositions/pion0269.asp",
            "http://www.assemblee-nationale.fr/15/ta-commission/r0269-a0.asp",
        ]

    def test_senat_pjl(self, texte_plfss2018_senat_premiere_lecture):
        from zam_repondeur.services.fetch.articles import get_possible_texte_urls

        assert get_possible_texte_urls(texte_plfss2018_senat_premiere_lecture) == [
            "https://www.senat.fr/leg/pjl17-063.html"
        ]

    def test_senat_ppl(self, db):
        from zam_repondeur.services.fetch.articles import get_possible_texte_urls
        from zam_repondeur.models import Chambre, Texte, TypeTexte

        with transaction.manager:
            texte = Texte.create(
                type_=TypeTexte.PROPOSITION,
                chambre=Chambre.SENAT,
                session=2017,
                numero=63,
                date_depot=date(2017, 10, 11),
            )

        assert get_possible_texte_urls(texte) == [
            "https://www.senat.fr/leg/ppl17-063.html"
        ]


class TestGetArticlesAN:
    @responses.activate
    def test_new_articles_are_created(self, app, lecture_an, amendements_an):
        from zam_repondeur.services.fetch.articles import get_articles
        from zam_repondeur.models import DBSession
        from zam_repondeur.models.events.article import (
            ContenuArticleModifie,
            TitreArticleModifie,
        )

        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
            body=(SAMPLE_DATA_DIR / "pl0269.html").read_text("utf-8", "ignore"),
            status=200,
        )

        DBSession.add(lecture_an)

        # We only have the article mentioned by the amendement
        assert {article.num for article in lecture_an.articles} == {"1"}

        changed = get_articles(lecture_an)

        assert changed

        # We now also have article 2 after scraping the web page
        assert {article.num for article in lecture_an.articles} == {"1", "2"}

        # Events should be created
        assert len(lecture_an.articles[0].events) == 2
        assert isinstance(lecture_an.articles[0].events[0], TitreArticleModifie)
        assert lecture_an.articles[0].events[0].created_at is not None
        assert lecture_an.articles[0].events[0].user is None
        assert lecture_an.articles[0].events[0].data["old_value"] == ""
        assert (
            lecture_an.articles[0].events[0].data["new_value"]
            == "Dispositions relatives l'exercice 2016"
        )
        assert isinstance(lecture_an.articles[0].events[1], ContenuArticleModifie)
        assert lecture_an.articles[0].events[1].created_at is not None
        assert lecture_an.articles[0].events[1].user is None
        assert lecture_an.articles[0].events[1].data["old_value"] == {}
        assert (
            lecture_an.articles[0].events[1].data["new_value"]["001"]
            == "Au titre de l'exercice 2016, sont approuvs :"
        )

    @responses.activate
    def test_article_ranges(self, app, lecture_an):
        from zam_repondeur.services.fetch.articles import get_articles
        from zam_repondeur.models import DBSession

        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
            body=(SAMPLE_DATA_DIR / "pl0387.html")
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
        from zam_repondeur.services.fetch.articles import get_articles
        from zam_repondeur.models import DBSession, Amendement

        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
            body=(SAMPLE_DATA_DIR / "pl0269.html").read_text("utf-8", "ignore"),
            status=200,
        )

        DBSession.add(lecture_an)

        amendement = DBSession.query(Amendement).filter(Amendement.num == "666").first()
        assert amendement.article.user_content.title == ""
        assert amendement.article.content == {}

        changed = get_articles(lecture_an)

        assert changed

        # We can get the article contents from an amendement
        amendement = DBSession.query(Amendement).filter(Amendement.num == "666").first()
        assert (
            amendement.article.user_content.title
            == "Dispositions relatives l'exercice 2016"
        )
        assert amendement.article.content["001"].startswith(
            "Au titre de l'exercice 2016"
        )

    @responses.activate
    def test_annexes_are_retrieved(self, app, lecture_an, amendements_an):
        from zam_repondeur.services.fetch.articles import get_articles
        from zam_repondeur.models import DBSession, Article

        lecture_an.texte.numero = 1056
        lecture_an.organe = "PO717460"
        lecture_an.titre = "Première lecture – Séance publique"
        DBSession.add(lecture_an)

        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/projets/pl1056.asp",
            status=404,
        )
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/propositions/pion1056.asp",
            status=404,
        )
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/ta-commission/r1056-a0.asp",
            body=(SAMPLE_DATA_DIR / "r1056-a0.html")
            .read_text("latin-1")
            .encode("latin-1"),
            status=200,
        )

        assert get_articles(lecture_an)

        annexe = DBSession.query(Article).filter(Article.type == "annexe").first()
        assert annexe.num == "93"
        assert (
            annexe.user_content.title
            == "Stratégie nationale d'orientation de l'action publique"
        )
        assert annexe.content["001"].startswith(
            "ANNEXE Stratégie nationale d'orientation de l'action publique"
        )
        assert annexe.content["002"].startswith(
            (
                "La présente stratégie nationale énonce les orientations et les "
                "objectifs de l'action publique vers une société de confiance, "
                "d'ici à 2022."
            )
        )

    @responses.activate
    def test_custom_article_titles_are_preserved(self, app, lecture_an, amendements_an):
        from zam_repondeur.services.fetch.articles import get_articles
        from zam_repondeur.models import DBSession, Amendement

        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
            body=(SAMPLE_DATA_DIR / "pl0269.html").read_text("utf-8", "ignore"),
            status=200,
        )

        DBSession.add(lecture_an)

        amendement = DBSession.query(Amendement).filter(Amendement.num == "666").first()
        assert amendement.article.user_content.title == ""
        assert amendement.article.content == {}

        # Let's set a custom article title
        amendement.article.user_content.title = "My custom title"

        changed = get_articles(lecture_an)

        assert changed

        # We can get the article contents from an amendement
        amendement = DBSession.query(Amendement).filter(Amendement.num == "666").first()
        assert amendement.article.user_content.title == "My custom title"
        assert amendement.article.content["001"].startswith(
            "Au titre de l'exercice 2016"
        )

    @responses.activate
    def test_intersticial_articles_are_not_updated(self, app, lecture_an):
        from zam_repondeur.services.fetch.articles import get_articles
        from zam_repondeur.models import DBSession, Article

        article_avant_2 = Article.create(
            lecture=lecture_an, type="article", num="2", pos="avant"
        )
        DBSession.add(article_avant_2)

        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
            body=(SAMPLE_DATA_DIR / "pl0269.html").read_text("utf-8", "ignore"),
            status=200,
        )

        changed = get_articles(lecture_an)

        assert changed

        article = DBSession.query(Article).filter(Article.pos == "avant").first()
        assert article.user_content.title == ""
        assert article.content == {}

    @responses.activate
    def test_fallback_to_alternative_url_pattern(
        self, app, dossier_plfss2018, lecture_an, amendements_an
    ):
        from zam_repondeur.services.fetch.articles import get_articles
        from zam_repondeur.models import DBSession, Amendement

        with transaction.manager:
            lecture_an.texte.numero = 575
            lecture_an.organe = "PO717460"
            lecture_an.titre = "Première lecture – Séance publique"

            amendements_an[0].article.num = "2"

            # The objects are no longer bound to a session here, as they were created in
            # a previous transaction, so we add them to the current session to make sure
            # that our changes will be committed with the current transaction
            DBSession.add(lecture_an)
            DBSession.add_all(amendements_an)

        # These URL patterns will fail
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/projets/pl0575.asp",
            status=404,
        )
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/propositions/pion0575.asp",
            status=404,
        )

        # So we want to use this one instead
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/ta-commission/r0575-a0.asp",
            body=(SAMPLE_DATA_DIR / "r0575-a0.html").read_text("utf-8", "ignore"),
            status=200,
        )

        with transaction.manager:
            DBSession.add(dossier_plfss2018)
            DBSession.add(lecture_an)
            changed = get_articles(lecture_an)

        assert changed

        amendement = DBSession.query(Amendement).filter(Amendement.num == "666").first()
        assert amendement.article.content["001"].startswith(
            "Le code des relations entre"
        )

    @responses.activate
    def test_not_found(self, app, lecture_an, amendements_an):
        from zam_repondeur.services.fetch.articles import get_articles
        from zam_repondeur.models import DBSession, Amendement

        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
            status=404,
        )
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/propositions/pion0269.asp",
            status=404,
        )
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/ta-commission/r0269-a0.asp",
            status=404,
        )

        changed = get_articles(lecture_an)

        assert not changed

        amendement = DBSession.query(Amendement).filter(Amendement.num == "666").first()
        assert amendement.article.content == {}


class TestGetArticlesSenat:
    @responses.activate
    def test_get_articles_senat(
        self, app, dossier_plfss2018, lecture_senat, amendements_senat, article1_an
    ):
        from zam_repondeur.services.fetch.articles import get_articles
        from zam_repondeur.models import DBSession, Amendement, Article
        from zam_repondeur.models.events.article import (
            ContenuArticleModifie,
            TitreArticleModifie,
        )

        responses.add(
            responses.GET,
            "https://www.senat.fr/leg/pjl17-063.html",
            body=(SAMPLE_DATA_DIR / "pjl17-063.html").read_text("utf-8", "ignore"),
            status=200,
        )

        with transaction.manager:
            DBSession.add(dossier_plfss2018)
            DBSession.add(lecture_senat)
            changed = get_articles(lecture_senat)

        assert changed

        amendement = (
            DBSession.query(Amendement).filter(Amendement.num == "6666").first()
        )
        assert amendement.article.content["001"].startswith(
            "Au titre de l'exercice 2016"
        )

        # We should not modify articles from unrelated lectures
        article = DBSession.query(Article).filter_by(pk=article1_an.pk).one()
        assert article is not amendement.article
        assert article.content == {}

        # Events should be created
        assert len(amendement.article.events) == 2
        assert isinstance(amendement.article.events[0], TitreArticleModifie)
        assert amendement.article.events[0].created_at is not None
        assert amendement.article.events[0].user is None
        assert amendement.article.events[0].data["old_value"] == ""
        assert (
            amendement.article.events[0].data["new_value"]
            == "Dispositions relatives à l'exercice 2016"
        )
        assert isinstance(amendement.article.events[1], ContenuArticleModifie)
        assert amendement.article.events[1].created_at is not None
        assert amendement.article.events[1].user is None
        assert amendement.article.events[1].data["old_value"] == {}
        assert (
            amendement.article.events[1].data["new_value"]["001"]
            == "Au titre de l'exercice 2016, sont approuvés :"
        )

    @responses.activate
    def test_get_articles_senat_with_mult(
        self, app, dossier_plfss2018, lecture_senat, amendements_senat
    ):
        from zam_repondeur.services.fetch.articles import get_articles
        from zam_repondeur.models import DBSession, Amendement

        responses.add(
            responses.GET,
            "https://www.senat.fr/leg/pjl17-063.html",
            body=(SAMPLE_DATA_DIR / "pjl17-063.html").read_text("utf-8", "ignore"),
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
            DBSession.add(dossier_plfss2018)
            DBSession.add(lecture_senat)
            changed = get_articles(lecture_senat)

        assert changed

        amendement = (
            DBSession.query(Amendement).filter(Amendement.num == "6666").first()
        )
        assert amendement.article.content["001"].startswith("Ne donnent pas lieu à")

    @responses.activate
    def test_get_articles_senat_with_dots(
        self, app, dossier_plfss2018, lecture_senat, amendements_senat
    ):
        from zam_repondeur.services.fetch.articles import get_articles
        from zam_repondeur.models import DBSession, Amendement

        responses.add(
            responses.GET,
            "https://www.senat.fr/leg/pjl17-063.html",
            body=(SAMPLE_DATA_DIR / "pjl17-659.html").read_text("utf-8", "ignore"),
            status=200,
        )

        with transaction.manager:
            DBSession.add(dossier_plfss2018)
            DBSession.add(lecture_senat)
            changed = get_articles(lecture_senat)

        assert changed

        amendement = (
            DBSession.query(Amendement).filter(Amendement.num == "6666").first()
        )
        assert amendement.article.content["001"].startswith("La stratégie nationale")

    @responses.activate
    def test_get_articles_missing_data(
        self, app, dossier_plfss2018, lecture_senat, amendements_senat, article1_an
    ):
        from zam_repondeur.services.fetch.articles import get_articles
        from zam_repondeur.models import DBSession, Amendement

        responses.add(
            responses.GET,
            "https://www.senat.fr/leg/pjl17-063.html",
            body=(SAMPLE_DATA_DIR / "pjl17-701.html").read_text("utf-8", "ignore"),
            status=200,
        )

        with transaction.manager:
            DBSession.add(dossier_plfss2018)
            DBSession.add(lecture_senat)
            changed = get_articles(lecture_senat)

        assert not changed

        amendement = (
            DBSession.query(Amendement).filter(Amendement.num == "6666").first()
        )
        assert amendement.article.content == {}

        # Events should NOT be created
        assert len(amendement.article.events) == 0

    @responses.activate
    def test_get_articles_tlfp_parse_error(
        self, app, dossier_plfss2018, lecture_senat, amendements_senat, article1_an
    ):
        from zam_repondeur.services.fetch.articles import get_articles
        from zam_repondeur.models import DBSession, Amendement

        responses.add(
            responses.GET,
            "https://www.senat.fr/leg/pjl17-063.html",
            body=(SAMPLE_DATA_DIR / "pjl18-218.html").read_text("utf-8", "ignore"),
            status=200,
        )

        with transaction.manager:
            DBSession.add(dossier_plfss2018)
            DBSession.add(lecture_senat)
            changed = get_articles(lecture_senat)

        assert not changed

        amendement = (
            DBSession.query(Amendement).filter(Amendement.num == "6666").first()
        )
        assert amendement.article.content == {}

        # Events should NOT be created
        assert len(amendement.article.events) == 0


def test_get_section_title():
    from zam_repondeur.services.fetch.articles import get_section_title

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
    from zam_repondeur.services.fetch.articles import get_section_title

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
    from zam_repondeur.services.fetch.articles import get_article_num_mult

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
        ("3 à 3 ter", [("3", ""), ("3", "bis"), ("3", "ter")]),
        ("4 ter à 4 quinquies", [("4", "ter"), ("4", "quater"), ("4", "quinquies")]),
    ],
)
def test_get_article_nums_mults(input, output):
    from zam_repondeur.services.fetch.articles import get_article_nums_mults

    assert get_article_nums_mults({"titre": input}) == output
