import pytest
import transaction


def test_select_all_not_visible_by_default(
    wsgi_server,
    driver,
    lecture_an,
    amendements_an,
    lecture_an_url,
    user_david,
    user_david_table_an,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendements_an[0])

    driver.get(f"{lecture_an_url}/tables/{user_david.email}")
    all_selected = driver.find_element_by_css_selector('[name="select-all"]')
    assert not all_selected.is_displayed()


def test_select_all_is_visible_with_filters(
    wsgi_server,
    driver,
    lecture_an,
    amendements_an,
    lecture_an_url,
    user_david,
    user_david_table_an,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendements_an[0])

    driver.get(f"{lecture_an_url}/tables/{user_david.email}")
    driver.find_element_by_link_text("Filtrer").click()
    all_selected = driver.find_element_by_css_selector('[name="select-all"]')
    assert all_selected.is_displayed()


def test_select_all_toggle_group_actions(
    wsgi_server,
    driver,
    lecture_an,
    amendements_an,
    lecture_an_url,
    user_david,
    user_david_table_an,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendements_an[0])

    driver.get(f"{lecture_an_url}/tables/{user_david.email}")
    driver.find_element_by_link_text("Filtrer").click()
    all_selected = driver.find_element_by_css_selector('[name="select-all"]')
    all_selected.click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert group_actions.is_displayed()
    all_selected.click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert not group_actions.is_displayed()


def test_select_all_change_transfer_url(
    wsgi_server,
    driver,
    lecture_an,
    amendements_an,
    lecture_an_url,
    user_david,
    user_david_table_an,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendements_an[0])
        user_david_table_an.add_amendement(amendements_an[1])

    driver.get(f"{lecture_an_url}/tables/{user_david.email}")
    driver.find_element_by_link_text("Filtrer").click()
    all_selected = driver.find_element_by_css_selector('[name="select-all"]')
    all_selected.click()
    transfer_amendements = driver.find_element_by_css_selector("#transfer-amendements")
    assert (
        transfer_amendements.get_attribute("href")
        == f"{lecture_an_url}/transfer_amendements?nums=666&nums=999"
    )


@pytest.mark.parametrize(
    "column_index,input_text,expected_nums",
    [("1", "1", "nums=666&nums=999"), ("2", "777", "nums=777")],
)
def test_select_all_checks_only_visible_amendements(
    wsgi_server,
    driver,
    lecture_an,
    lecture_an_url,
    article7bis_an,
    amendements_an,
    user_david,
    user_david_table_an,
    column_index,
    input_text,
    expected_nums,
):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        DBSession.add_all(amendements_an)
        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendements_an[0])
        user_david_table_an.add_amendement(amendements_an[1])
        amendement = Amendement.create(
            lecture=lecture_an, article=article7bis_an, num=777
        )
        user_david_table_an.add_amendement(amendement)

    driver.get(f"{lecture_an_url}/tables/{user_david.email}")
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
        == f"{lecture_an_url}/transfer_amendements?{expected_nums}"
    )
