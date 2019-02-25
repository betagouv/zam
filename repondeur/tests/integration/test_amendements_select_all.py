import pytest
import transaction


def test_select_all_not_visible_by_default(
    wsgi_server, driver, lecture_an, amendements_an
):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    all_selected = driver.find_element_by_css_selector('[name="select-all"]')
    assert not all_selected.is_displayed()


def test_select_all_is_visible_with_filters(
    wsgi_server, driver, lecture_an, amendements_an
):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    driver.find_element_by_link_text("Filtrer").click()
    all_selected = driver.find_element_by_css_selector('[name="select-all"]')
    assert all_selected.is_displayed()


def test_select_all_toggle_group_actions(
    wsgi_server, driver, lecture_an, amendements_an
):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    driver.find_element_by_link_text("Filtrer").click()
    all_selected = driver.find_element_by_css_selector('[name="select-all"]')
    all_selected.click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert group_actions.is_displayed()
    all_selected.click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert not group_actions.is_displayed()


def test_select_all_change_transfer_url(
    wsgi_server, driver, lecture_an, amendements_an
):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    driver.find_element_by_link_text("Filtrer").click()
    all_selected = driver.find_element_by_css_selector('[name="select-all"]')
    all_selected.click()
    transfer_amendements = driver.find_element_by_css_selector("#transfer-amendements")
    assert (
        transfer_amendements.get_attribute("href")
        == f"{LECTURE_URL}/transfer_amendements?from_index=1&nums=666&nums=999"
    )


@pytest.mark.parametrize(
    "column_index,input_text,expected_nums",
    [
        ("2", "1", "nums=666&nums=999"),
        ("3", "777", "nums=777"),
        ("4", "Da", "nums=999&nums=777"),
    ],
)
def test_select_all_checks_only_visible_amendements(
    wsgi_server,
    driver,
    lecture_an,
    article7bis_an,
    amendements_an,
    user_david,
    user_ronan,
    user_daniel,
    column_index,
    input_text,
    expected_nums,
):
    from zam_repondeur.models import Amendement, DBSession

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    with transaction.manager:
        DBSession.add_all(amendements_an)
        table_ronan = user_ronan.table_for(lecture_an)
        table_ronan.amendements.append(amendements_an[0])
        table_david = user_david.table_for(lecture_an)
        table_david.amendements.append(amendements_an[1])
        amendement = Amendement.create(
            lecture=lecture_an, article=article7bis_an, num=777
        )
        table_daniel = user_daniel.table_for(lecture_an)
        table_daniel.amendements.append(amendement)

    driver.get(f"{LECTURE_URL}/amendements")
    driver.find_element_by_link_text("Filtrer").click()
    input_field = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) input"
    )
    input_field.send_keys(input_text)
    all_selected = driver.find_element_by_css_selector('[name="select-all"]')
    all_selected.click()
    transfer_amendements = driver.find_element_by_css_selector("#transfer-amendements")
    assert (
        transfer_amendements.get_attribute("href")
        == f"{LECTURE_URL}/transfer_amendements?from_index=1&{expected_nums}"
    )
