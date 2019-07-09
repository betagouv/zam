import transaction


def test_visionneuse_article(wsgi_server, driver, lecture_an, amendements_an):
    LECTURE_URL = f"{wsgi_server.application_url}{lecture_an.url}"
    driver.get(f"{LECTURE_URL}/articles/")
    articles = driver.find_elements_by_css_selector("section.article")
    assert len(articles) == 1
    assert articles[0].find_element_by_css_selector("h2").text == "Article 1"


def test_visionneuse_articles(
    wsgi_server, driver, lecture_an, article7bis_an, amendements_an
):
    from zam_repondeur.models import DBSession

    LECTURE_URL = f"{wsgi_server.application_url}{lecture_an.url}"
    with transaction.manager:
        amendements_an[0].article = article7bis_an
        DBSession.add_all(amendements_an)

    driver.get(f"{LECTURE_URL}/articles/")
    articles = driver.find_elements_by_css_selector("section.article")
    assert len(articles) == 2
    assert articles[0].find_element_by_css_selector("h2").text == "Article 1"
    assert articles[1].find_element_by_css_selector("h2").text == "Article 7 bis"
