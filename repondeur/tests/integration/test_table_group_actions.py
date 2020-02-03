import pytest
import transaction
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

pytestmark = pytest.mark.flaky(max_runs=5)


def test_group_actions_not_visible_by_default(
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
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert not group_actions.is_displayed()
    batch_amendements = driver.find_element_by_css_selector("#batch-amendements")
    assert not batch_amendements.is_displayed()


def test_group_actions_are_visible_by_selection(
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
    driver.find_element_by_css_selector('[name="amendement-selected"]').click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert group_actions.is_displayed()
    batch_amendements = driver.find_element_by_css_selector("#batch-amendements")
    assert not batch_amendements.is_displayed()


def test_batch_amendements_are_visible_with_at_least_two_selections(
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
    checkboxes = driver.find_elements_by_css_selector('[name="amendement-selected"]')
    checkboxes[0].click()
    checkboxes[1].click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert group_actions.is_displayed()
    batch_amendements = driver.find_element_by_css_selector("#batch-amendements")
    assert batch_amendements.is_displayed()


def test_batch_amendements_is_hidden_when_selected_amendements_have_different_articles(
    wsgi_server,
    driver,
    lecture_an,
    article7bis_an,
    amendements_an,
    lecture_an_url,
    user_david,
    user_david_table_an,
):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        amendement = Amendement.create(
            lecture=lecture_an, article=article7bis_an, num=777
        )
        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendements_an[0])
        user_david_table_an.add_amendement(amendements_an[1])
        user_david_table_an.add_amendement(amendement)

    driver.get(f"{lecture_an_url}/tables/{user_david.email}")
    checkboxes = driver.find_elements_by_css_selector('[name="amendement-selected"]')
    checkboxes[0].click()
    checkboxes[1].click()
    checkboxes[2].click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert group_actions.is_displayed()
    batch_amendements = driver.find_element_by_css_selector("#batch-amendements")
    assert not batch_amendements.is_displayed()


def test_batch_amendements_is_hidden_when_selected_amendements_have_different_missions(
    wsgi_server,
    driver,
    lecture_an,
    article1_an,
    amendements_an,
    lecture_an_url,
    user_david,
    user_david_table_an,
):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        mission1_titre = "Mission 1"
        amendements_an[0].mission_titre = amendements_an[
            1
        ].mission_titre = mission1_titre

        mission2_titre = "Mission 2"
        amendement = Amendement.create(
            lecture=lecture_an,
            article=article1_an,
            mission_titre=mission2_titre,
            num=777,
        )

        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendements_an[0])
        user_david_table_an.add_amendement(amendements_an[1])
        user_david_table_an.add_amendement(amendement)

    driver.get(f"{lecture_an_url}/tables/{user_david.email}")
    checkboxes = driver.find_elements_by_css_selector('[name="amendement-selected"]')
    checkboxes[0].click()
    checkboxes[1].click()
    checkboxes[2].click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert group_actions.is_displayed()
    batch_amendements = driver.find_element_by_css_selector("#batch-amendements")
    assert not batch_amendements.is_displayed()


def test_group_actions_are_made_invisible_by_unselection(
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
    driver.find_element_by_css_selector('[name="amendement-selected"]').click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert group_actions.is_displayed()
    driver.find_element_by_css_selector('[name="amendement-selected"]').click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert not group_actions.is_displayed()


def test_group_actions_button_urls_change_with_selection(
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
    find = driver.find_element_by_css_selector

    checkboxes = driver.find_elements_by_css_selector('[name="amendement-selected"]')
    checkboxes[0].click()

    WebDriverWait(driver, 20).until(EC.visibility_of(find(".groupActions")))

    assert find(".groupActions").is_displayed()

    for action in ["transfer-amendements", "export-pdf"]:
        assert (
            find("#" + action).get_attribute("href")
            == f"{lecture_an_url}/{action.replace('-', '_')}?n=666"
        )

    checkboxes[1].click()

    for action in ["transfer-amendements", "export-pdf"]:
        assert (
            find("#" + action).get_attribute("href")
            == f"{lecture_an_url}/{action.replace('-', '_')}?n=666&n=999"
        )

    checkboxes[0].click()

    for action in ["transfer-amendements", "export-pdf"]:
        assert (
            find("#" + action).get_attribute("href")
            == f"{lecture_an_url}/{action.replace('-', '_')}?n=999"
        )

    checkboxes[1].click()

    for action in ["transfer-amendements", "export-pdf"]:
        assert (
            find("#" + action).get_attribute("href")
            == f"{lecture_an_url}/{action.replace('-', '_')}"
        )

    assert not find(".groupActions").is_displayed()


def test_group_actions_button_urls_change_on_the_fly(
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
        == f"{lecture_an_url}/transfer_amendements?n=666"
    )

    transfer_link.click()
    assert driver.current_url == (
        f"{lecture_an_url}/transfer_amendements?n=666&"
        f"back=%2Fdossiers%2F{lecture_an.dossier.url_key}"
        f"%2Flectures%2F{lecture_an.url_key}%2Ftables%2Fdavid%40exemple.gouv.fr"
        f"%3Farticle%3D1"
    )
