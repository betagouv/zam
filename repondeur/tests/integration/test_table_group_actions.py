import pytest
import transaction

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


pytestmark = pytest.mark.flaky(max_runs=5)


def test_group_actions_not_visible_by_default(
    wsgi_server, driver, lecture_an, amendements_an
):
    from zam_repondeur.models import DBSession, User

    email = "user@example.com"
    with transaction.manager:
        user = DBSession.query(User).filter(User.email == email).first()
        table = user.table_for(lecture_an)
        table.amendements.append(amendements_an[0])

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/tables/{email}")
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert not group_actions.is_displayed()
    batch_amendements = driver.find_element_by_css_selector("#batch-amendements")
    assert not batch_amendements.is_displayed()


def test_group_actions_are_visible_by_selection(
    wsgi_server, driver, lecture_an, amendements_an
):
    from zam_repondeur.models import DBSession, User

    email = "user@example.com"
    with transaction.manager:
        user = DBSession.query(User).filter(User.email == email).first()
        table = user.table_for(lecture_an)
        table.amendements.append(amendements_an[0])

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/tables/{email}")
    driver.find_element_by_css_selector('[name="amendement-selected"]').click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert group_actions.is_displayed()
    batch_amendements = driver.find_element_by_css_selector("#batch-amendements")
    assert not batch_amendements.is_displayed()


def test_batch_amendements_are_visible_with_at_least_two_selections(
    wsgi_server, driver, lecture_an, amendements_an
):
    from zam_repondeur.models import DBSession, User

    email = "user@example.com"
    with transaction.manager:
        user = DBSession.query(User).filter(User.email == email).first()
        table = user.table_for(lecture_an)
        table.amendements.append(amendements_an[0])
        table.amendements.append(amendements_an[1])

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/tables/{email}")
    checkboxes = driver.find_elements_by_css_selector('[name="amendement-selected"]')
    checkboxes[0].click()
    checkboxes[1].click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert group_actions.is_displayed()
    batch_amendements = driver.find_element_by_css_selector("#batch-amendements")
    assert batch_amendements.is_displayed()


def test_batch_amendements_are_visible_with_at_least_two_selections_if_same_article(
    wsgi_server, driver, lecture_an, article7bis_an, amendements_an
):
    from zam_repondeur.models import Amendement, DBSession, User

    email = "user@example.com"
    with transaction.manager:
        amendement = Amendement.create(
            lecture=lecture_an, article=article7bis_an, num=777
        )
        user = DBSession.query(User).filter(User.email == email).first()
        table = user.table_for(lecture_an)
        table.amendements.append(amendements_an[0])
        table.amendements.append(amendements_an[1])
        table.amendements.append(amendement)

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/tables/{email}")
    checkboxes = driver.find_elements_by_css_selector('[name="amendement-selected"]')
    checkboxes[0].click()
    checkboxes[1].click()
    checkboxes[2].click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert group_actions.is_displayed()
    batch_amendements = driver.find_element_by_css_selector("#batch-amendements")
    assert not batch_amendements.is_displayed()


def test_group_actions_are_made_invisible_by_unselection(
    wsgi_server, driver, lecture_an, amendements_an
):
    from zam_repondeur.models import DBSession, User

    email = "user@example.com"
    with transaction.manager:
        user = DBSession.query(User).filter(User.email == email).first()
        table = user.table_for(lecture_an)
        table.amendements.append(amendements_an[0])

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/tables/{email}")
    driver.find_element_by_css_selector('[name="amendement-selected"]').click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert group_actions.is_displayed()
    driver.find_element_by_css_selector('[name="amendement-selected"]').click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert not group_actions.is_displayed()


def test_group_actions_button_urls_change_with_selection(
    wsgi_server, driver, lecture_an, amendements_an
):
    from zam_repondeur.models import DBSession, User

    email = "user@example.com"
    with transaction.manager:
        user = DBSession.query(User).filter(User.email == email).first()
        table = user.table_for(lecture_an)
        table.amendements.append(amendements_an[0])
        table.amendements.append(amendements_an[1])

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/tables/{email}")
    find = driver.find_element_by_css_selector

    checkboxes = driver.find_elements_by_css_selector('[name="amendement-selected"]')
    checkboxes[0].click()

    WebDriverWait(driver, 20).until(EC.visibility_of(find(".groupActions")))

    assert find(".groupActions").is_displayed()

    for action in ["transfer-amendements", "export-pdf"]:
        assert (
            find("#" + action).get_attribute("href")
            == f"{LECTURE_URL}/{action.replace('-', '_')}?nums=666"
        )

    checkboxes[1].click()

    for action in ["transfer-amendements", "export-pdf"]:
        assert (
            find("#" + action).get_attribute("href")
            == f"{LECTURE_URL}/{action.replace('-', '_')}?nums=666&nums=999"
        )

    checkboxes[0].click()

    for action in ["transfer-amendements", "export-pdf"]:
        assert (
            find("#" + action).get_attribute("href")
            == f"{LECTURE_URL}/{action.replace('-', '_')}?nums=999"
        )

    checkboxes[1].click()

    for action in ["transfer-amendements", "export-pdf"]:
        assert (
            find("#" + action).get_attribute("href")
            == f"{LECTURE_URL}/{action.replace('-', '_')}"
        )

    assert not find(".groupActions").is_displayed()


def test_group_actions_button_urls_change_on_the_fly(
    wsgi_server, driver, lecture_an, amendements_an
):
    from zam_repondeur.models import DBSession, User

    email = "user@example.com"
    with transaction.manager:
        user = DBSession.query(User).filter(User.email == email).first()
        table = user.table_for(lecture_an)
        table.amendements.append(amendements_an[0])
        table.amendements.append(amendements_an[1])

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/tables/{email}")
    find = driver.find_element_by_css_selector
    driver.find_element_by_link_text("Filtrer").click()

    # Set a filter on the article
    input_field = find(f"thead tr.filters th:nth-child(1) input")
    input_field.send_keys("1")
    # Select the first amendement
    checkboxes = driver.find_elements_by_css_selector('[name="amendement-selected"]')
    checkboxes[0].click()

    transfer_link = find("#transfer-amendements")
    assert (
        transfer_link.get_attribute("href")
        == f"{LECTURE_URL}/transfer_amendements?nums=666"
    )

    transfer_link.click()
    assert driver.current_url == (
        f"{LECTURE_URL}/transfer_amendements?nums=666&"
        f"back=%2Flectures%2F{lecture_an.url_key}%2Ftables%2Fuser%40example.com"
        f"%3Farticle%3D1"
    )
