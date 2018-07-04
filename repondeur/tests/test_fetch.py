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


@responses.activate
def test_get_articles(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.fetch import get_articles
    from zam_repondeur.models import DBSession, Amendement, Lecture

    responses.add(
        responses.GET,
        "https://www.senat.fr/leg/pjl17-063.html",
        body=(Path(__file__).parent / "sample_data" / "pjl17-063.html").read_text(
            "utf-8", "ignore"
        ),
        status=200,
    )
    with transaction.manager:
        lecture = Lecture.get(
            chambre=dummy_lecture[0],
            session=dummy_lecture[1],
            num_texte=dummy_lecture[2],
        )
        lecture.chambre = "senat"
        lecture.session = "2017-2018"
        lecture.num_texte = 63

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        amendement.chambre = "senat"
        amendement.session = "2017-2018"
        amendement.num_texte = 63

        get_articles(lecture)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.subdiv_contenu["001"].startswith("Au titre de l'exercice 2016")


@responses.activate
def test_get_articles_with_mult(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.fetch import get_articles
    from zam_repondeur.models import DBSession, Amendement, Lecture

    responses.add(
        responses.GET,
        "https://www.senat.fr/leg/pjl17-063.html",
        body=(Path(__file__).parent / "sample_data" / "pjl17-063.html").read_text(
            "utf-8", "ignore"
        ),
        status=200,
    )
    with transaction.manager:
        lecture = Lecture.get(
            chambre=dummy_lecture[0],
            session=dummy_lecture[1],
            num_texte=dummy_lecture[2],
        )
        lecture.chambre = "senat"
        lecture.session = "2017-2018"
        lecture.num_texte = 63

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        amendement.chambre = "senat"
        amendement.session = "2017-2018"
        amendement.num_texte = 63
        amendement.subdiv_num = "4"
        amendement.subdiv_mult = "bis"

        get_articles(lecture)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.subdiv_contenu["001"].startswith("Ne donnent pas lieu à")


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
        ("2", "2", ""),
        ("1er", "1", ""),
        ("3 bis", "3", "bis"),
        ("5 ter AAA", "5", "ter AAA"),
    ],
)
def test_get_article_num_mult(input, num, mult):
    from zam_repondeur.fetch import get_article_num_mult

    assert get_article_num_mult({"titre": input}) == (num, mult)
