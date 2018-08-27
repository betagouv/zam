import pytest


@pytest.mark.parametrize(
    "type_,pos,num,mult,output",
    [
        ("article", "", "1", "", "Art. 1"),
        ("annexe", "", "1", "", "Annexe 1"),
        ("article", "", "1", "bis", "Art. 1 bis"),
        ("article", "avant", "1", "", "Avant art. 1"),
    ],
)
def test_article_disp(type_, pos, num, mult, output):
    from zam_repondeur.models import Article

    article = Article.create(type=type_, num=num, mult=mult, pos=pos)
    assert str(article) == output
