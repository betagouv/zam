import transaction


def test_repondeur_does_not_contains_link_to_visionneuse_if_no_avis(
    wsgi_server, driver, lecture_an, amendements_an
):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    menu_items = [
        item.text for item in driver.find_elements_by_css_selector("nav.main li")
    ]
    assert "Dossier de banc" not in menu_items


def test_repondeur_contains_link_to_visionneuse_if_avis(
    wsgi_server, driver, lecture_an, amendements_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendements_an[0].user_content.avis = "Favorable"
        DBSession.add_all(amendements_an)

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    menu_items = [
        item.text for item in driver.find_elements_by_css_selector("nav.main li")
    ]
    assert "Dossier de banc" in menu_items


def test_column_filtering_changes_edit_url_on_the_fly(
    wsgi_server, driver, lecture_an, amendements_an
):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    input_field = driver.find_element_by_css_selector(
        "thead tr.filters th:nth-child(3) input"
    )
    input_field.send_keys("666")
    assert driver.current_url == f"{LECTURE_URL}/amendements?amendement=666"
    see_td = driver.find_element_by_css_selector("td:nth-child(7)")
    see_link = see_td.find_element_by_css_selector("a")
    assert (
        see_link.get_attribute("href")
        == f"{LECTURE_URL}/amendements/666/amendement_edit"
    )
    see_link.click()
    assert driver.current_url == (
        f"{LECTURE_URL}/amendements/666/amendement_edit?"
        f"back=%2Flectures%2F{lecture_an.url_key}%2Famendements%3Famendement%3D666"
    )
