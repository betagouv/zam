from time import sleep

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait


def test_amendements_search(wsgi_server, driver, lecture_an_url, amendements_an):
    url = f"{lecture_an_url}/amendements/"
    driver.get(url)
    driver.find_element_by_link_text("Accès amendement").click()
    assert driver.find_element_by_css_selector("#search-amendements").is_displayed()
    driver.find_element_by_css_selector("#q-amendement").send_keys(
        f"{amendements_an[0].num}{Keys.ENTER}"
    )
    wait = WebDriverWait(driver, 1)
    wait.until(lambda driver: driver.current_url != url)
    assert driver.current_url == f"{url}?article=article.1..#amdt-666"


def test_amendements_search_not_found(
    wsgi_server, driver, lecture_an_url, amendements_an
):
    driver.get(f"{lecture_an_url}/amendements/")
    assert not driver.find_element_by_css_selector(
        "#search-amendements .error"
    ).is_displayed()
    driver.find_element_by_link_text("Accès amendement").click()
    driver.find_element_by_css_selector("#q-amendement").send_keys(f"42{Keys.ENTER}")
    sleep(1)  # Wait for the AJAX request.
    assert driver.find_element_by_css_selector(
        "#search-amendements .error"
    ).is_displayed()
