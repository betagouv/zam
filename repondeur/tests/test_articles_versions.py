import transaction


def test_versions_are_created_on_mult_update_with_history(app, article1_an):
    from zam_repondeur.models import Article, DBSession

    with transaction.manager:
        article1_an.mult = "bis"
        DBSession.add(article1_an)

    article = DBSession.query(Article).filter(Article.num == article1_an.num).first()
    assert article.mult == "bis"
    assert article.version == 2
    ArticleHistory = Article.__history_mapper__.class_
    first_version = (
        DBSession.query(ArticleHistory).filter(ArticleHistory.version == 1).first()
    )
    assert first_version.mult == ""
