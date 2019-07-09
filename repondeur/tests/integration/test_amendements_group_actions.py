def test_group_actions_not_visible_by_default(
    wsgi_server, driver, lecture_an_url, amendements_an
):
    driver.get(f"{lecture_an_url}/amendements")
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert not group_actions.is_displayed()


def test_group_actions_are_visible_by_selection(
    wsgi_server, driver, lecture_an_url, amendements_an
):
    driver.get(f"{lecture_an_url}/amendements")
    driver.find_element_by_css_selector('[name="amendement-selected"]').click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert group_actions.is_displayed()


def test_group_actions_are_made_invisible_by_unselection(
    wsgi_server, driver, lecture_an_url, amendements_an
):
    driver.get(f"{lecture_an_url}/amendements")
    driver.find_element_by_css_selector('[name="amendement-selected"]').click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert group_actions.is_displayed()
    driver.find_element_by_css_selector('[name="amendement-selected"]').click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert not group_actions.is_displayed()


def test_group_actions_button_urls_change_with_selection(
    wsgi_server, driver, lecture_an_url, amendements_an
):
    driver.get(f"{lecture_an_url}/amendements")
    find = driver.find_element_by_css_selector

    checkboxes = driver.find_elements_by_css_selector('[name="amendement-selected"]')
    checkboxes[0].click()

    assert find(".groupActions").is_displayed()

    assert (
        find("#transfer-amendements").get_attribute("href")
        == f"{lecture_an_url}/transfer_amendements?from_index=1&nums=666"
    )
    assert (
        find("#export-pdf").get_attribute("href")
        == f"{lecture_an_url}/export_pdf?nums=666"
    )

    checkboxes[1].click()

    assert (
        find("#transfer-amendements").get_attribute("href")
        == f"{lecture_an_url}/transfer_amendements?from_index=1&nums=666&nums=999"
    )
    assert (
        find("#export-pdf").get_attribute("href")
        == f"{lecture_an_url}/export_pdf?nums=666&nums=999"
    )

    checkboxes[0].click()

    assert (
        find("#transfer-amendements").get_attribute("href")
        == f"{lecture_an_url}/transfer_amendements?from_index=1&nums=999"
    )
    assert (
        find("#export-pdf").get_attribute("href")
        == f"{lecture_an_url}/export_pdf?nums=999"
    )

    checkboxes[1].click()

    assert (
        find("#transfer-amendements").get_attribute("href")
        == f"{lecture_an_url}/transfer_amendements?from_index=1"
    )
    assert find("#export-pdf").get_attribute("href") == f"{lecture_an_url}/export_pdf"

    assert not find(".groupActions").is_displayed()


def test_group_actions_button_urls_change_on_the_fly(
    wsgi_server, driver, lecture_an, lecture_an_url, amendements_an
):
    driver.get(f"{lecture_an_url}/amendements")
    find = driver.find_element_by_css_selector

    # Set a filter on the article
    input_field = find(f"thead tr.filters th:nth-child(2) input")
    input_field.send_keys("1")
    # Select the first amendement
    checkboxes = driver.find_elements_by_css_selector('[name="amendement-selected"]')
    checkboxes[0].click()

    transfer_link = find("#transfer-amendements")
    assert (
        transfer_link.get_attribute("href")
        == f"{lecture_an_url}/transfer_amendements?from_index=1&nums=666"
    )

    transfer_link.click()
    assert driver.current_url == (
        f"{lecture_an_url}/transfer_amendements?from_index=1&nums=666&"
        f"back=%2Fdossiers%2F{lecture_an.dossier.url_key}"
        f"%2Flectures%2F{lecture_an.url_key}%2Famendements%3Farticle%3D1"
    )
