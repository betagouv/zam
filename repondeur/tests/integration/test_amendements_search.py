from time import sleep

import transaction
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait


def test_amendements_search(wsgi_server, driver, lecture_an_url, amendements_an):
    url = f"{lecture_an_url}/amendements/"
    driver.get(url)
    input_field = driver.find_element_by_css_selector(
        "thead tr.filters th:nth-child(3) input"
    )
    input_field.send_keys("111")  # Unknown numero.
    wait = WebDriverWait(driver, 1)
    wait.until(lambda driver: driver.current_url != url)
    filter_url = driver.current_url
    assert driver.find_element_by_css_selector(
        '[data-target="amendement-search.form"]'
    ).is_displayed()
    driver.find_element_by_css_selector("#q-amendement").send_keys(
        f"{amendements_an[0].num}{Keys.ENTER}"
    )
    wait.until(lambda driver: driver.current_url != filter_url)
    assert driver.current_url == f"{url}?article=all#amdt-666"


def test_amendements_search_too_many(
    wsgi_server,
    settings,
    driver,
    lecture_an,
    article1_an,
    lecture_an_url,
    amendements_an,
):
    from zam_repondeur.models import Amendement

    nb_amendements = int(settings["zam.limits.max_amendements_for_full_index"])

    with transaction.manager:
        for i in range(nb_amendements):
            Amendement.create(lecture=lecture_an, article=article1_an, num=i + 1)

    url = f"{lecture_an_url}/amendements/"
    driver.get(url)
    input_field = driver.find_element_by_css_selector(
        "thead tr.filters th:nth-child(3) input"
    )
    input_field.send_keys("111")  # Unknown numero.
    wait = WebDriverWait(driver, 1)
    wait.until(lambda driver: driver.current_url != url)
    filter_url = driver.current_url
    assert driver.find_element_by_css_selector(
        '[data-target="amendement-search.form"]'
    ).is_displayed()
    driver.find_element_by_css_selector("#q-amendement").send_keys(
        f"{amendements_an[0].num}{Keys.ENTER}"
    )
    wait = WebDriverWait(driver, 1)
    wait.until(lambda driver: driver.current_url != filter_url)
    assert driver.current_url == f"{url}?article=article.1..#amdt-666"


def test_amendements_search_not_found(
    wsgi_server, driver, lecture_an_url, amendements_an
):
    driver.get(f"{lecture_an_url}/amendements/")
    assert not driver.find_element_by_css_selector(
        '[data-target="amendement-search.form"] .error'
    ).is_displayed()
    input_field = driver.find_element_by_css_selector(
        "thead tr.filters th:nth-child(3) input"
    )
    input_field.send_keys("111")  # Unknown numero.
    driver.find_element_by_css_selector("#q-amendement").send_keys(f"42{Keys.ENTER}")
    sleep(1)  # Wait for the AJAX request.
    assert driver.find_element_by_css_selector(
        '[data-target="amendement-search.form"] .error'
    ).is_displayed()
