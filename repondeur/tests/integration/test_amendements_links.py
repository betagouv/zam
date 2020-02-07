def test_repondeur_does_not_contains_link_to_visionneuse(
    wsgi_server, driver, lecture_an_url, amendements_an
):
    driver.get(f"{lecture_an_url}/amendements/")
    driver.find_element_by_css_selector(".menu-toggle").click()
    menu_items = [
        item.text for item in driver.find_elements_by_css_selector("nav.main li")
    ]
    assert "Dossier de banc" in menu_items


def test_column_filtering_changes_edit_url_on_the_fly(
    wsgi_server, driver, lecture_an, lecture_an_url, amendements_an
):
    driver.get(f"{lecture_an_url}/amendements/")
    input_field = driver.find_element_by_css_selector(
        "thead tr.filters th:nth-child(3) input"
    )
    input_field.send_keys("666")
    assert driver.current_url == f"{lecture_an_url}/amendements/?amendement=666"
    see_td = driver.find_element_by_css_selector("td:nth-child(7)")
    see_link = see_td.find_element_by_css_selector("a")
    assert (
        see_link.get_attribute("href")
        == f"{lecture_an_url}/amendements/666/amendement_edit"
    )
    see_link.click()
    assert driver.current_url == (
        f"{lecture_an_url}/amendements/666/amendement_edit?"
        f"back=%2Fdossiers%2F{lecture_an.dossier.url_key}"
        f"%2Flectures%2F{lecture_an.url_key}%2Famendements%2F%3Famendement%3D666"
    )
