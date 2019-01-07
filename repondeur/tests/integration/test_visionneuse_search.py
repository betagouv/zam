import transaction

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait


def test_visionneuse_articles_search(
    wsgi_server, driver, lecture_an, article7bis_an, amendements_an
):
    from zam_repondeur.models import DBSession

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    with transaction.manager:
        amendements_an[0].article = article7bis_an
        DBSession.add_all(amendements_an)

    driver.get(f"{LECTURE_URL}/articles/")
    articles = driver.find_elements_by_css_selector("section.article")
    assert len(articles) == 2
    assert articles[0].find_element_by_css_selector("h2").text == "Article 1"
    assert articles[0].is_displayed()
    assert articles[1].find_element_by_css_selector("h2").text == "Article 7 bis"
    assert articles[1].is_displayed()
    driver.find_element_by_css_selector("#q-article").send_keys(f"1{Keys.ENTER}")
    articles = driver.find_elements_by_css_selector("section.article")
    assert len(articles) == 2
    assert articles[0].is_displayed()
    assert not articles[1].is_displayed()


def test_visionneuse_articles_search_not_found(
    wsgi_server, driver, lecture_an, amendements_an
):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/articles/")
    articles = driver.find_elements_by_css_selector("section.article")
    assert len(articles) == 1
    assert articles[0].is_displayed()
    assert not driver.find_element_by_css_selector(
        "#search-article .error"
    ).is_displayed()
    driver.find_element_by_css_selector("#q-article").send_keys(f"42{Keys.ENTER}")
    articles = driver.find_elements_by_css_selector("section.article")
    assert len(articles) == 1
    assert articles[0].is_displayed()
    assert driver.find_element_by_css_selector("#search-article .error").is_displayed()


def test_visionneuse_amendements_search(
    wsgi_server, driver, lecture_an, article7bis_an, amendements_an
):
    from zam_repondeur.models import DBSession

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    with transaction.manager:
        amendements_an[0].user_content.avis = "Favorable"
        DBSession.add_all(amendements_an)

    url = f"{LECTURE_URL}/articles/"
    driver.get(url)
    driver.find_element_by_link_text("Accès amendement").click()
    driver.find_element_by_css_selector("#q-amendement").send_keys(
        f"{amendements_an[0].num}{Keys.ENTER}"
    )
    wait = WebDriverWait(driver, 1)
    wait.until(lambda driver: driver.current_url != url)
    assert driver.current_url == f"{url}article.1../reponses#amdt-666"


def test_visionneuse_amendements_search_not_found(
    wsgi_server, driver, lecture_an, amendements_an
):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/articles/")
    assert not driver.find_element_by_css_selector(
        "#search-amendements .error"
    ).is_displayed()
    driver.find_element_by_link_text("Accès amendement").click()
    driver.find_element_by_css_selector("#q-amendement").send_keys(f"42{Keys.ENTER}")
    assert driver.find_element_by_css_selector(
        "#search-amendements .error"
    ).is_displayed()
