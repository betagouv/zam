import time
from textwrap import dedent

import transaction
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


def test_amendement_creation_select_article(
    wsgi_server, driver, lecture_conseil_ccfp_url, articles_conseil_ccfp
):
    driver.get(f"{lecture_conseil_ccfp_url}/amendements/saisie")
    subdiv = Select(driver.find_element_by_css_selector('select[name="subdiv"]'))
    subdiv.select_by_visible_text("Art. 2")
    time.sleep(1)  # Wait for the option to be selected.

    assert (
        driver.find_element_by_css_selector('[data-target="preview.contents"]').text
        == dedent(
            """
            001
            Contenu article 2 alinéa 1
            002
            Contenu article 2 alinéa 2
        """
        ).strip()
    )


def test_amendement_creation(
    wsgi_server, driver, lecture_conseil_ccfp_url, articles_conseil_ccfp
):
    from zam_repondeur.models import DBSession, Amendement

    driver.get(f"{lecture_conseil_ccfp_url}/amendements/saisie")
    subdiv = Select(driver.find_element_by_css_selector('select[name="subdiv"]'))
    subdiv.select_by_visible_text("Art. 2")

    groupe = Select(driver.find_element_by_css_selector('select[name="groupe"]'))
    groupe.select_by_visible_text("CFTC")

    driver.switch_to.frame("corps_ifr")
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-id="corps"]',))
    ).send_keys("Corps")

    driver.switch_to.default_content()  # Required to be able to switch to a new iframe.

    driver.switch_to.frame("expose_ifr")
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-id="expose"]',))
    ).send_keys("Exposé")

    driver.switch_to.default_content()
    save_button = driver.find_element_by_css_selector(
        '.save-buttons input[name="save"]'
    )
    save_button.click()

    with transaction.manager:
        amendement = DBSession.query(Amendement).first()
        assert amendement.groupe == "CFTC"
        assert amendement.article.num == "2"
        assert amendement.corps == "<p>Corps</p>"
        assert amendement.expose == "<p>Exposé</p>"
