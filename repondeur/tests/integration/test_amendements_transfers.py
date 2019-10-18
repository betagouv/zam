import pytest
import transaction

pytestmark = pytest.mark.flaky(max_runs=5)


def test_transfer_amendements_switch_color_on_check_from_inactive_user(
    wsgi_server,
    driver,
    users_repository,  # Useful to reset users' activities.
    amendements_repository,  # Useful to reset amendements' edits.
    team_zam,
    user_david,
    user_ronan,
    user_david_table_an,
    lecture_an_url,
    amendements_an,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(team_zam)
        team_zam.users.append(user_ronan)
        DBSession.add(user_david_table_an)
        # We put the amendement on another table.
        user_david_table_an.add_amendement(amendements_an[0])
        DBSession.add_all(amendements_an)

    driver.get(f"{lecture_an_url}/transfer_amendements?nums={amendements_an[0].num}")

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


def test_transfer_amendements_switch_color_on_check_from_edited_amendement(
    wsgi_server,
    driver,
    users_repository,  # Useful to reset users' activities.
    amendements_repository,  # Useful to reset amendements' edits.
    team_zam,
    user_david,
    user_ronan,
    user_david_table_an,
    user_ronan_table_an,
    lecture_an_url,
    amendements_an,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(team_zam)
        team_zam.users.append(user_ronan)
        user_ronan.record_activity()
        DBSession.add(user_ronan_table_an)
        # We put the amendement on another active user table,
        user_ronan_table_an.add_amendement(amendements_an[0])
        # and we start editing it.
        amendements_an[0].start_editing()
        DBSession.add_all(amendements_an)

    driver.get(f"{lecture_an_url}/transfer_amendements?nums={amendements_an[0].num}")

    checkbox = driver.find_element_by_css_selector('input[type="checkbox"]')
    submit_button = driver.find_element_by_css_selector('input[name="submit-to"]')
    submit_index_button = driver.find_element_by_css_selector(
        'input[name="submit-index"]'
    )

    # The amendement being edited, the checkbox is not checked by default.
    assert not checkbox.is_selected()
    assert submit_button.get_attribute("class") == "button primary enabled"
    assert submit_index_button.get_attribute("class") == "button primary"

    # If we check the amendement while being edited, we are in danger.
    checkbox.click()
    assert submit_button.get_attribute("class") == "button enabled danger"
    assert submit_index_button.get_attribute("class") == "button danger"

    # If we uncheck back, the danger class is not anymore useful.
    checkbox.click()
    assert submit_button.get_attribute("class") == "button enabled primary"
    assert submit_index_button.get_attribute("class") == "button primary"


def test_transfer_amendements_switch_color_on_check_from_edited_an_unedited_amendements(
    wsgi_server,
    driver,
    users_repository,  # Useful to reset users' activities.
    amendements_repository,  # Useful to reset amendements' edits.
    team_zam,
    user_david,
    user_ronan,
    user_daniel,
    user_david_table_an,
    user_ronan_table_an,
    user_daniel_table_an,
    lecture_an_url,
    amendements_an,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(team_zam)
        team_zam.users.append(user_ronan)
        team_zam.users.append(user_daniel)
        user_ronan.record_activity()
        DBSession.add(user_david_table_an)
        DBSession.add(user_ronan_table_an)
        DBSession.add(user_daniel_table_an)
        # We put the amendement on another active user table,
        user_ronan_table_an.add_amendement(amendements_an[0])
        # and we start editing it.
        amendements_an[0].start_editing()
        # We put the amendement on another inactive user table.
        user_daniel_table_an.add_amendement(amendements_an[1])
        DBSession.add_all(amendements_an)

    driver.get(
        f"{lecture_an_url}/transfer_amendements?"
        f"nums={amendements_an[0].num}&nums={amendements_an[1].num}"
    )

    checkbox_active, checkbox_inactive = driver.find_elements_by_css_selector(
        'input[type="checkbox"]'
    )
    submit_button = driver.find_element_by_css_selector('input[name="submit-to"]')
    submit_index_button = driver.find_element_by_css_selector(
        'input[name="submit-index"]'
    )

    # The amendement being edited, the checkbox is not checked by default,
    assert not checkbox_active.is_selected()
    # But the second one is given that it is not being edited,
    assert checkbox_inactive.is_selected()
    # And thus the set class is warning on load.
    assert submit_button.get_attribute("class") == "button enabled warning"
    assert submit_index_button.get_attribute("class") == "button warning"

    # If we check the amendement being edited, we are in danger.
    checkbox_active.click()
    assert submit_button.get_attribute("class") == "button enabled danger"
    assert submit_index_button.get_attribute("class") == "button danger"

    # If we uncheck the amendement which is not being edited, we are still in danger.
    checkbox_inactive.click()
    assert submit_button.get_attribute("class") == "button enabled danger"
    assert submit_index_button.get_attribute("class") == "button danger"

    # If we uncheck the amendement being edited, we are back at primary.
    checkbox_active.click()
    assert submit_button.get_attribute("class") == "button enabled primary"
    assert submit_index_button.get_attribute("class") == "button primary"

    # If we check the amendement which is not being edited, we are back at warning.
    checkbox_inactive.click()
    assert submit_button.get_attribute("class") == "button enabled warning"
    assert submit_index_button.get_attribute("class") == "button warning"
