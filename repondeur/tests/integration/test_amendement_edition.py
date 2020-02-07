import time

import pytest
import transaction
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


def test_amendement_edition_start_editing_status(
    wsgi_server, driver, lecture_an, amendements_an, lecture_an_url, user_david_table_an
):
    from zam_repondeur.models import DBSession

    amendement = amendements_an[0]
    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendement)
        DBSession.add(amendement)

    assert not amendement.is_being_edited

    driver.get(f"{lecture_an_url}/amendements/{amendements_an[0].num}/amendement_edit")
    avis = Select(driver.find_element_by_css_selector('select[name="avis"]'))
    avis.select_by_visible_text("Défavorable")
    time.sleep(1)  # Wait for the option to be selected.

    assert amendement.is_being_edited


def test_amendement_edition_exit_stop_editing_status(
    wsgi_server, driver, lecture_an, amendements_an, lecture_an_url, user_david_table_an
):
    from zam_repondeur.models import DBSession

    amendement = amendements_an[0]
    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendement)
        DBSession.add(amendement)

    assert not amendement.is_being_edited

    driver.get(f"{lecture_an_url}/amendements/{amendements_an[0].num}/amendement_edit")
    avis = Select(driver.find_element_by_css_selector('select[name="avis"]'))
    avis.select_by_visible_text("Défavorable")
    time.sleep(1)  # Wait for the option to be selected.

    assert amendement.is_being_edited

    exit_link = driver.find_element_by_css_selector(".save-buttons a.arrow-left")
    exit_link.click()
    driver.switch_to.alert.accept()
    time.sleep(1)  # Wait for the alert to actually redirect.

    assert not amendement.is_being_edited


def test_amendement_edition_with_avis(
    wsgi_server, driver, lecture_an, amendements_an, lecture_an_url, user_david_table_an
):
    from zam_repondeur.models import Amendement, DBSession

    amendement = amendements_an[0]
    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendement)
        DBSession.add(amendement)

    driver.get(f"{lecture_an_url}/amendements/{amendements_an[0].num}/amendement_edit")
    avis = Select(driver.find_element_by_css_selector('select[name="avis"]'))
    avis.select_by_visible_text("Défavorable")
    save_button = driver.find_element_by_css_selector(
        '.save-buttons input[name="save"]'
    )
    save_button.click()

    with pytest.raises(NoAlertPresentException):
        driver.switch_to.alert

    with transaction.manager:
        amendements_an = DBSession.query(Amendement).all()
        assert amendements_an[0].user_content.avis == "Défavorable"


def test_amendement_edition_with_avis_and_reponse(
    wsgi_server, driver, lecture_an, amendements_an, lecture_an_url, user_david_table_an
):
    from zam_repondeur.models import Amendement, DBSession

    amendement = amendements_an[0]
    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendement)
        DBSession.add(amendement)

    driver.get(f"{lecture_an_url}/amendements/{amendements_an[0].num}/amendement_edit")
    avis = Select(driver.find_element_by_css_selector('select[name="avis"]'))
    avis.select_by_visible_text("Défavorable")

    driver.switch_to.frame("reponse_ifr")
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-id="reponse"]',))
    ).send_keys("Réponse")

    driver.switch_to.default_content()
    save_button = driver.find_element_by_css_selector(
        '.save-buttons input[name="save"]'
    )
    save_button.click()

    with pytest.raises(NoAlertPresentException):
        driver.switch_to.alert

    with transaction.manager:
        amendements_an = DBSession.query(Amendement).all()
        assert amendements_an[0].user_content.avis == "Défavorable"
        assert amendements_an[0].user_content.reponse == "<p>Réponse</p>"


def test_amendement_edition_with_reponse_only_and_accept(
    wsgi_server, driver, lecture_an, amendements_an, lecture_an_url, user_david_table_an
):
    from zam_repondeur.models import Amendement, DBSession

    amendement = amendements_an[0]
    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendement)
        DBSession.add(amendement)

    driver.get(f"{lecture_an_url}/amendements/{amendements_an[0].num}/amendement_edit")

    driver.switch_to.frame("reponse_ifr")
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-id="reponse"]',))
    ).send_keys("Réponse")

    driver.switch_to.default_content()
    save_button = driver.find_element_by_css_selector(
        '.save-buttons input[name="save"]'
    )
    save_button.click()
    driver.switch_to.alert.accept()
    time.sleep(1)  # Wait for the alert acceptation.

    with transaction.manager:
        amendements_an = DBSession.query(Amendement).all()
        assert amendements_an[0].user_content.reponse == "<p>Réponse</p>"

    assert driver.current_url == (
        f"{lecture_an_url}/tables/david@exemple.gouv.fr/"
        f"#amdt-{amendements_an[0].num}"
    )


def test_amendement_edition_with_reponse_only_and_deny(
    wsgi_server, driver, lecture_an, amendements_an, lecture_an_url, user_david_table_an
):
    from zam_repondeur.models import Amendement, DBSession

    amendement = amendements_an[0]
    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendement)
        DBSession.add(amendement)

    driver.get(f"{lecture_an_url}/amendements/{amendements_an[0].num}/amendement_edit")

    driver.switch_to.frame("reponse_ifr")
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-id="reponse"]',))
    ).send_keys("Réponse")

    driver.switch_to.default_content()
    save_button = driver.find_element_by_css_selector(
        '.save-buttons input[name="save"]'
    )
    save_button.click()
    driver.switch_to.alert.dismiss()
    time.sleep(1)  # Wait for the alert dismiss.

    with transaction.manager:
        amendements_an = DBSession.query(Amendement).all()
        assert amendements_an[0].user_content.reponse is None

    assert (
        driver.current_url
        == f"{lecture_an_url}/amendements/{amendements_an[0].num}/amendement_edit"
    )
