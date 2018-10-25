from itertools import tee

import pytest

from zam_repondeur.models import Article


def pairwise(iterable):
    """
    From https://docs.python.org/3/library/itertools.html#itertools-recipes
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


@pytest.mark.parametrize(
    "type_,pos,num,mult,output",
    [
        ("article", "", "0", "", "Art. liminaire"),
        ("article", "", "1", "", "Art. 1"),
        ("annexe", "", "1", "", "Annexe 1"),
        ("article", "", "1", "A", "Art. 1 A"),
        ("article", "", "1", "bis", "Art. 1 bis"),
        ("article", "", "1", "bis AA", "Art. 1 bis AA"),
        ("article", "avant", "1", "", "Avant art. 1"),
        ("article", "après", "1", "", "Après art. 1"),
        ("chapitre", "", "III", "", "Chapitre III"),
    ],
)
def test_stringify(lecture_an, type_, pos, num, mult, output):
    article = Article.create(
        lecture=lecture_an, type=type_, num=num, mult=mult, pos=pos
    )
    assert str(article) == output


@pytest.mark.parametrize(
    "type_,pos,num,mult,output",
    [
        ("article", "", "0", "", "article-0"),
        ("article", "", "1", "", "article-1"),
        ("annexe", "", "1", "", "annexe-1"),
        ("article", "", "1", "A", "article-1-a"),
        ("article", "", "1", "bis", "article-1-bis"),
        ("article", "", "1", "bis AA", "article-1-bis-aa"),
        ("article", "avant", "1", "", "article-add-av-1"),
        ("article", "après", "1", "", "article-add-ap-1"),
        ("chapitre", "", "III", "", "chapitre-iii"),
    ],
)
def test_slug(lecture_an, type_, pos, num, mult, output):
    article = Article.create(
        lecture=lecture_an, type=type_, num=num, mult=mult, pos=pos
    )
    assert article.slug == output


@pytest.mark.parametrize(
    "type_,pos,num,mult,output",
    [
        ("article", "", "0", "", "Article liminaire"),
        ("article", "", "1", "", "Article 1"),
        ("annexe", "", "1", "", "Annexe 1"),
        ("annexe", "", "1", "A", "Annexe 1 A"),
        ("article", "", "1", "bis", "Article 1 bis"),
        ("article", "", "1", "bis AA", "Article 1 bis AA"),
        ("article", "avant", "1", "", "Article add. av. 1"),
        ("article", "après", "1", "", "Article add. ap. 1"),
        ("chapitre", "", "III", "", "Chapitre III"),
    ],
)
def test_format(lecture_an, type_, pos, num, mult, output):
    article = Article.create(
        lecture=lecture_an, type=type_, num=num, mult=mult, pos=pos
    )
    assert article.format(short=False) == output


class TestOrdering:
    def test_types(self, lecture_an):
        titre = Article.create(lecture=lecture_an, type="titre")
        motion = Article.create(lecture=lecture_an, type="motion")
        chapitre = Article.create(lecture=lecture_an, type="chapitre")
        section = Article.create(lecture=lecture_an, type="section")
        sous_section = Article.create(lecture=lecture_an, type="sous-section")
        article = Article.create(lecture=lecture_an, type="article")
        annexe = Article.create(lecture=lecture_an, type="annexe")
        vide = Article.create(lecture=lecture_an, type="")
        assert (
            titre < motion < chapitre < section < sous_section < article < annexe < vide
        )

    @pytest.mark.parametrize(
        "before, after",
        list(
            pairwise(
                [
                    "11",
                    "11 bis A",
                    "11 bis",
                    "11 ter",
                    "11 quater",
                    "11 quinquies",
                    "11 sexies",
                    "12 AA",
                    "12 AB",
                    "12 A",
                    "12 BA",
                    "12 BB",
                    "12 BC",
                    "12 BD",
                    "12 B",
                    "12 C",
                    "12 D",
                    "12",
                    "12 bis",
                    "13",
                    "13 bis",
                    "13 ter",
                    "13 quater A",
                    "13 quater",
                    "13 quinquies",
                    "13 sexies",
                    "14",
                    "14 bis A",
                    "14 bis",
                    "15",
                    "16",
                    "17",
                    "17 bis AAA",
                    "17 bis AA",
                    "17 bis A",
                    "17 bis BA",
                    "17 bis BB",
                    "17 bis B",
                    "17 bis C",
                    "17 bis",
                    "17 ter",
                ]
            )
        ),
    )
    def test_andouillette(self, lecture_an, before, after):
        """
        Examples from https://www.senat.fr/dossier-legislatif/tc/tc_pjl03-328.html
        """

        def make_article(s):
            if " " in s:
                num, mult = s.split(" ", 1)
            else:
                num, mult = s, ""
            return Article.create(
                lecture=lecture_an, type="article", num=num, mult=mult
            )

        assert make_article(before) < make_article(after)

    def test_avant_apres(self, lecture_an):
        article_6 = Article.create(lecture=lecture_an, type="article", num=6)
        apres_article_6 = Article.create(
            lecture=lecture_an, type="article", num=6, pos="après"
        )
        avant_article_7 = Article.create(
            lecture=lecture_an, type="article", num=7, pos="avant"
        )
        article_7 = Article.create(lecture=lecture_an, type="article", num=7)

        assert article_6 < apres_article_6 < avant_article_7 < article_7

    def test_previous_next(self, lecture_an):
        article_6 = Article.create(lecture=lecture_an, type="article", num=6)
        apres_article_6 = Article.create(
            lecture=lecture_an, type="article", num=6, pos="après"
        )
        avant_article_7 = Article.create(
            lecture=lecture_an, type="article", num=7, pos="avant"
        )
        article_7 = Article.create(lecture=lecture_an, type="article", num=7)

        assert article_6.previous_article is None
        assert article_6.next_article == apres_article_6
        assert apres_article_6.previous_article == article_6
        assert apres_article_6.next_article == avant_article_7
        assert avant_article_7.previous_article == apres_article_6
        assert avant_article_7.next_article == article_7
        assert article_7.previous_article == avant_article_7
        assert article_7.next_article is None

    def test_previous_next_displayable(self, article1_an, lecture_an, amendements_an):
        from zam_repondeur.models import DBSession

        article_6 = Article.create(lecture=lecture_an, type="article", num=6)
        apres_article_6 = Article.create(
            lecture=lecture_an, type="article", num=6, pos="après"
        )
        avant_article_7 = Article.create(
            lecture=lecture_an, type="article", num=7, pos="avant"
        )
        article_7 = Article.create(lecture=lecture_an, type="article", num=7)
        amendements_an[0].article = avant_article_7
        amendements_an[0].avis = "Favorable"
        DBSession.add_all(amendements_an)

        assert article1_an.previous_displayable_article is None
        assert article1_an.next_displayable_article == article_6
        assert article_6.previous_displayable_article == article1_an
        assert article_6.next_displayable_article == avant_article_7
        assert apres_article_6.previous_displayable_article == article_6
        assert apres_article_6.next_displayable_article == avant_article_7
        assert avant_article_7.previous_displayable_article == article_6
        assert avant_article_7.next_displayable_article == article_7
        assert article_7.previous_displayable_article == avant_article_7
        assert article_7.next_displayable_article is None
