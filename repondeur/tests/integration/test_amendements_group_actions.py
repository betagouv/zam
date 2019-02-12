def test_group_actions_not_visible_by_default(
    wsgi_server, driver, lecture_an, amendements_an
):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert not group_actions.is_displayed()


def test_group_actions_are_visible_by_selection(
    wsgi_server, driver, lecture_an, amendements_an
):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    driver.find_element_by_css_selector('[name="amendement-selected"]').click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert group_actions.is_displayed()


def test_group_actions_are_made_invisible_by_unselection(
    wsgi_server, driver, lecture_an, amendements_an
):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    driver.find_element_by_css_selector('[name="amendement-selected"]').click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert group_actions.is_displayed()
    driver.find_element_by_css_selector('[name="amendement-selected"]').click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert not group_actions.is_displayed()


def test_group_actions_button_urls_change_with_selection(
    wsgi_server, driver, lecture_an, amendements_an
):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    checkboxes = driver.find_elements_by_css_selector('[name="amendement-selected"]')
    checkboxes[0].click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert group_actions.is_displayed()

    for action in ["transfer-amendements", "export-pdf"]:
        button = driver.find_element_by_css_selector("#" + action)
        assert (
            button.get_attribute("href")
            == f"{LECTURE_URL}/{action.replace('-', '_')}?nums=666"
        )

    checkboxes[1].click()

    for action in ["transfer-amendements", "export-pdf"]:
        button = driver.find_element_by_css_selector("#" + action)
        assert (
            button.get_attribute("href")
            == f"{LECTURE_URL}/{action.replace('-', '_')}?nums=666&nums=999"
        )

    checkboxes[0].click()
    for action in ["transfer-amendements", "export-pdf"]:
        button = driver.find_element_by_css_selector("#" + action)
        assert (
            button.get_attribute("href")
            == f"{LECTURE_URL}/{action.replace('-', '_')}?nums=999"
        )

    checkboxes[1].click()

    for action in ["transfer-amendements", "export-pdf"]:
        button = driver.find_element_by_css_selector("#" + action)
        assert (
            button.get_attribute("href") == f"{LECTURE_URL}/{action.replace('-', '_')}"
        )

    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert not group_actions.is_displayed()
