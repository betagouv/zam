def test_column_sorting_once_changes_url(wsgi_server, browser, lecture_an):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    browser.get(f"{LECTURE_URL}/amendements")
    header = browser.find_element_by_css_selector("th")
    header.click()
    assert browser.current_url == f"{LECTURE_URL}/amendements?sort=1asc"


def test_column_sorting_twice_changes_url_direction(wsgi_server, browser, lecture_an):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    browser.get(f"{LECTURE_URL}/amendements")
    header = browser.find_element_by_css_selector("th")
    header.click()
    header.click()
    assert browser.current_url == f"{LECTURE_URL}/amendements?sort=1desc"


def test_column_sorting_thrice_changes_url_again(wsgi_server, browser, lecture_an):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    browser.get(f"{LECTURE_URL}/amendements")
    header = browser.find_element_by_css_selector("th")
    header.click()
    header.click()
    header.click()
    assert browser.current_url == f"{LECTURE_URL}/amendements?sort=1asc"


def test_column_sorting_is_cancelable(wsgi_server, browser, lecture_an):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    browser.get(f"{LECTURE_URL}/amendements")
    header = browser.find_element_by_css_selector("th")
    header.click()
    assert browser.current_url == f"{LECTURE_URL}/amendements?sort=1asc"
    cancel = browser.find_element_by_css_selector("#unsort")
    cancel.click()
    assert browser.current_url == f"{LECTURE_URL}/amendements"
