import transaction


def test_transfer_amendements_switch_color_on_check_from_inactive_user(
    wsgi_server,
    driver,
    users_repository,  # Useful to reset users' activities.
    user_david,
    user_david_table_an,
    lecture_an,
    amendements_an,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        # We put the amendement on another table.
        user_david_table_an.amendements.append(amendements_an[0])
        DBSession.add_all(amendements_an)

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/transfer_amendements?nums={amendements_an[0].num}")

    checkbox = driver.find_element_by_css_selector('input[type="checkbox"]')
    submit_button = driver.find_element_by_css_selector('input[name="submit-to"]')
    submit_index_button = driver.find_element_by_css_selector(
        'input[name="submit-index"]'
    )

    # The amendement being on another table, it is checked and there is a warning class.
    assert checkbox.is_selected()
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


def test_transfer_amendements_switch_color_on_check_from_active_user(
    wsgi_server,
    driver,
    users_repository,  # Useful to reset users' activities.
    user_david,
    user_david_table_an,
    lecture_an,
    amendements_an,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        user_david.record_activity()
        DBSession.add(user_david_table_an)
        # We put the amendement on another active user table.
        user_david_table_an.amendements.append(amendements_an[0])
        DBSession.add_all(amendements_an)

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/transfer_amendements?nums={amendements_an[0].num}")

    checkbox = driver.find_element_by_css_selector('input[type="checkbox"]')
    submit_button = driver.find_element_by_css_selector('input[name="submit-to"]')
    submit_index_button = driver.find_element_by_css_selector(
        'input[name="submit-index"]'
    )

    # The amendement being on another active user table, the checkbox is not checked.
    assert not checkbox.is_selected()
    assert submit_button.get_attribute("class") == "button primary enabled"
    assert submit_index_button.get_attribute("class") == "button primary"

    # If we check the amendement on another active user table, we are in danger.
    checkbox.click()
    assert submit_button.get_attribute("class") == "button enabled danger"
    assert submit_index_button.get_attribute("class") == "button danger"

    # If we uncheck back, the danger class is not anymore useful.
    checkbox.click()
    assert submit_button.get_attribute("class") == "button enabled primary"
    assert submit_index_button.get_attribute("class") == "button primary"


def test_transfer_amendements_switch_color_on_check_from_active_and_inactive_users(
    wsgi_server,
    driver,
    users_repository,  # Useful to reset users' activities.
    user_david,
    user_david_table_an,
    user_ronan_table_an,
    lecture_an,
    amendements_an,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        user_david.record_activity()
        DBSession.add(user_david_table_an)
        DBSession.add(user_ronan_table_an)
        # We put the amendement on another active user table.
        user_david_table_an.amendements.append(amendements_an[0])
        # We put the amendement on another inactive user table.
        user_ronan_table_an.amendements.append(amendements_an[1])
        DBSession.add_all(amendements_an)

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(
        f"{LECTURE_URL}/transfer_amendements?"
        f"nums={amendements_an[0].num}&nums={amendements_an[1].num}"
    )

    checkbox_active, checkbox_inactive = driver.find_elements_by_css_selector(
        'input[type="checkbox"]'
    )
    submit_button = driver.find_element_by_css_selector('input[name="submit-to"]')
    submit_index_button = driver.find_element_by_css_selector(
        'input[name="submit-index"]'
    )

    # The amendement being on another active user table, the checkbox is not checked,
    assert not checkbox_active.is_selected()
    # But the second one is from an inactive user so it is,
    assert checkbox_inactive.is_selected()
    # And thus the set class is warning on load.
    assert submit_button.get_attribute("class") == "button enabled warning"
    assert submit_index_button.get_attribute("class") == "button warning"

    # If we check the amendement on another active user table, we are in danger.
    checkbox_active.click()
    assert submit_button.get_attribute("class") == "button enabled danger"
    assert submit_index_button.get_attribute("class") == "button danger"

    # If we uncheck the amendement on inactive user table, we are still in danger.
    checkbox_inactive.click()
    assert submit_button.get_attribute("class") == "button enabled danger"
    assert submit_index_button.get_attribute("class") == "button danger"

    # If we uncheck the amendement on active user table, we are back at primary.
    checkbox_active.click()
    assert submit_button.get_attribute("class") == "button enabled primary"
    assert submit_index_button.get_attribute("class") == "button primary"

    # If we check the amendement on active user table, we are back at warning.
    checkbox_inactive.click()
    assert submit_button.get_attribute("class") == "button enabled warning"
    assert submit_index_button.get_attribute("class") == "button warning"
