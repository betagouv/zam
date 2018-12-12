import transaction


def test_versions_are_created_on_mult_update(app, article1_an):
    from zam_repondeur.models import Article, ArticleRevision, DBSession

    with transaction.manager:
        article1_an.mult = "bis"
        DBSession.add(article1_an)

    article = DBSession.query(Article).filter(Article.num == article1_an.num).first()
    assert article.mult == "bis"
    assert len(article.revisions) == 1  # mult update
    assert article.revisions[0].mult == ""
    revision = (
        DBSession.query(ArticleRevision)
        .filter(ArticleRevision.num == article1_an.num)
        .first()
    )
    assert revision.mult == ""
    assert revision.article.mult == "bis"


def test_versions_are_created_on_mult_and_pos_update(app, article1_an):
    from zam_repondeur.models import Article, ArticleRevision, DBSession

    with transaction.manager:
        article1_an.mult = "bis"
        article1_an.pos = "avant"
        DBSession.add(article1_an)

    article = DBSession.query(Article).filter(Article.num == article1_an.num).first()
    assert article.mult == "bis"
    assert article.pos == "avant"
    assert len(article.revisions) == 1 + 1  # mult update + pos update
    assert article.revisions[0].mult == ""
    assert article.revisions[1].mult == "bis"
    assert article.revisions[0].pos == ""
    assert article.revisions[1].pos == ""
    revision = (
        DBSession.query(ArticleRevision)
        .filter(ArticleRevision.num == article1_an.num)
        .first()
    )
    assert revision.mult == ""
    assert revision.pos == ""
    assert revision.article.mult == "bis"
    assert revision.article.pos == "avant"
