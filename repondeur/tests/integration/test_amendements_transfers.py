import transaction


def test_transfer_amendements_switch_color_on_check(
    wsgi_server, driver, user_david_table_senat, lecture_an, amendements_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david_table_senat)
        # We put the amendement on another table.
        user_david_table_senat.amendements.append(amendements_an[0])
        DBSession.add_all(amendements_an)

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/transfer_amendements?nums={amendements_an[0].num}")

    checkbox = driver.find_element_by_css_selector('input[type="checkbox"]')
    submit_button = driver.find_element_by_css_selector('input[name="submit"]')
    submit_index_button = driver.find_element_by_css_selector(
        'input[name="submit-index"]'
    )

    # The amendement being on another table, there is a warning class.
    assert submit_button.get_attribute("class") == "button enabled warning"
    assert submit_index_button.get_attribute("class") == "button warning"

    # If we uncheck the amendement on another table, classes are back to normal.
    checkbox.click()
    assert submit_button.get_attribute("class") == "button enabled primary"
    assert submit_index_button.get_attribute("class") == "button primary"

    # If we check again, the warning class is back.
    checkbox.click()
    assert submit_button.get_attribute("class") == "button enabled warning"
    assert submit_index_button.get_attribute("class") == "button warning"
