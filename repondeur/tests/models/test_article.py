import pytest

from zam_repondeur.models import Article


@pytest.mark.parametrize(
    "type_,pos,num,mult,output",
    [
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
