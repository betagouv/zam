import transaction


def test_versions_are_created_on_title_update(app, article1_an):
    from zam_repondeur.models import Article, ArticleUserContentRevision, DBSession

    with transaction.manager:
        DBSession.add(article1_an)
        article1_an.user_content.title = "modified"
        DBSession.add(article1_an)

    article = DBSession.query(Article).filter(Article.num == article1_an.num).first()
    assert article.user_content.title == "modified"
    assert len(article.user_content.revisions) == 1  # title update
    assert article.user_content.revisions[0].title == ""
    revision = (
        DBSession.query(ArticleUserContentRevision)
        .filter(ArticleUserContentRevision.article == article1_an)
        .first()
    )
    assert revision.title == ""
    assert revision.user_content.title == "modified"


def test_versions_are_created_on_title_and_presentation_update(app, article1_an):
    from zam_repondeur.models import Article, ArticleUserContentRevision, DBSession

    with transaction.manager:
        DBSession.add(article1_an)
        article1_an.user_content.title = "modified"
        article1_an.user_content.presentation = "Présentation"
        DBSession.add(article1_an)

    article = DBSession.query(Article).filter(Article.num == article1_an.num).first()
    assert article.user_content.title == "modified"
    assert article.user_content.presentation == "Présentation"
    assert len(article.user_content.revisions) == 1 + 1  # title + presentation update
    assert article.user_content.revisions[0].title == ""
    assert article.user_content.revisions[1].title == "modified"
    assert article.user_content.revisions[0].presentation == ""
    assert article.user_content.revisions[1].presentation == ""
    revision = (
        DBSession.query(ArticleUserContentRevision)
        .filter(ArticleUserContentRevision.article == article1_an)
        .first()
    )
    assert revision.title == ""
    assert revision.presentation == ""
    assert revision.user_content.title == "modified"
    assert revision.user_content.presentation == "Présentation"
