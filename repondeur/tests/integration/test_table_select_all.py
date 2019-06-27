import pytest
import transaction


def test_select_all_not_visible_by_default(
    wsgi_server, driver, lecture_an, amendements_an
):
    from zam_repondeur.models import DBSession, User

    email = "user@exemple.gouv.fr"
    with transaction.manager:
        user = DBSession.query(User).filter(User.email == email).first()
        table = user.table_for(lecture_an)
        table.amendements.append(amendements_an[0])

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/tables/{email}")
    all_selected = driver.find_element_by_css_selector('[name="select-all"]')
    assert not all_selected.is_displayed()


def test_select_all_is_visible_with_filters(
    wsgi_server, driver, lecture_an, amendements_an
):
    from zam_repondeur.models import DBSession, User

    email = "user@exemple.gouv.fr"
    with transaction.manager:
        user = DBSession.query(User).filter(User.email == email).first()
        table = user.table_for(lecture_an)
        table.amendements.append(amendements_an[0])

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/tables/{email}")
    driver.find_element_by_link_text("Filtrer").click()
    all_selected = driver.find_element_by_css_selector('[name="select-all"]')
    assert all_selected.is_displayed()


def test_select_all_toggle_group_actions(
    wsgi_server, driver, lecture_an, amendements_an
):
    from zam_repondeur.models import DBSession, User

    email = "user@exemple.gouv.fr"
    with transaction.manager:
        user = DBSession.query(User).filter(User.email == email).first()
        table = user.table_for(lecture_an)
        table.amendements.append(amendements_an[0])

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/tables/{email}")
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
    from zam_repondeur.models import DBSession, User

    email = "user@exemple.gouv.fr"
    with transaction.manager:
        user = DBSession.query(User).filter(User.email == email).first()
        table = user.table_for(lecture_an)
        table.amendements.append(amendements_an[0])
        table.amendements.append(amendements_an[1])

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/tables/{email}")
    driver.find_element_by_link_text("Filtrer").click()
    all_selected = driver.find_element_by_css_selector('[name="select-all"]')
    all_selected.click()
    transfer_amendements = driver.find_element_by_css_selector("#transfer-amendements")
    assert (
        transfer_amendements.get_attribute("href")
        == f"{LECTURE_URL}/transfer_amendements?nums=666&nums=999"
    )


@pytest.mark.parametrize(
    "column_index,input_text,expected_nums",
    [("1", "1", "nums=666&nums=999"), ("2", "777", "nums=777")],
)
def test_select_all_checks_only_visible_amendements(
    wsgi_server,
    driver,
    lecture_an,
    article7bis_an,
    amendements_an,
    column_index,
    input_text,
    expected_nums,
):
    from zam_repondeur.models import Amendement, DBSession, User

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    email = "user@exemple.gouv.fr"
    with transaction.manager:
        DBSession.add_all(amendements_an)
        user = DBSession.query(User).filter(User.email == email).first()
        table = user.table_for(lecture_an)
        table.amendements.append(amendements_an[0])
        table.amendements.append(amendements_an[1])
        amendement = Amendement.create(
            lecture=lecture_an, article=article7bis_an, num=777
        )
        table.amendements.append(amendement)

    driver.get(f"{LECTURE_URL}/tables/{email}")
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
        == f"{LECTURE_URL}/transfer_amendements?{expected_nums}"
    )
