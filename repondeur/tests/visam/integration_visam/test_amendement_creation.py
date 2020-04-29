import time
from textwrap import dedent

import transaction
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


def test_amendement_creation_select_article(
    driver, user_ccfp, lecture_seance_ccfp_url, articles_seance_ccfp
):
    driver.login(user_ccfp.email)
    driver.get(f"{lecture_seance_ccfp_url}/amendements/saisie")
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


class TestAddAmendement:
    def test_member_adds_amendement_for_their_organization(
        app,
        driver,
        lecture_seance_ccfp_url,
        articles_seance_ccfp,
        user_ccfp,
        org_gouvernement,
        org_cgt,
    ):
        from zam_repondeur.models import DBSession, Amendement

        driver.login(user_ccfp.email)
        driver.get(f"{lecture_seance_ccfp_url}/amendements/saisie")
        subdiv = Select(driver.find_element_by_css_selector('select[name="subdiv"]'))
        subdiv.select_by_visible_text("Art. 2")

        driver.switch_to.frame("corps_ifr")
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-id="corps"]',))
        ).send_keys("Corps")

        driver.switch_to.default_content()  # Required to switch to a new iframe.

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
            assert amendement.num == "CGT 1"
            assert amendement.groupe == "CGT"
            assert amendement.article.num == "2"
            assert amendement.corps == "<p>Corps</p>"
            assert amendement.expose == "<p>Exposé</p>"

    def test_gouvernement_adds_amendement_for_an_organization(
        app,
        driver,
        lecture_seance_ccfp_url,
        articles_seance_ccfp,
        user_gouvernement,
        org_gouvernement,
        org_cgt,
    ):
        from zam_repondeur.models import DBSession, Amendement

        driver.login(user_gouvernement.email)
        driver.get(f"{lecture_seance_ccfp_url}/amendements/saisie")
        subdiv = Select(driver.find_element_by_css_selector('select[name="subdiv"]'))
        subdiv.select_by_visible_text("Art. 2")

        organisation = Select(
            driver.find_element_by_css_selector('select[name="organisation"]')
        )
        organisation.select_by_visible_text("CGT")

        driver.switch_to.frame("corps_ifr")
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-id="corps"]',))
        ).send_keys("Corps")

        driver.switch_to.default_content()  # Required to switch to a new iframe.

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
            assert amendement.num == "CGT 1"
            assert amendement.groupe == "CGT"
            assert amendement.article.num == "2"
            assert amendement.corps == "<p>Corps</p>"
            assert amendement.expose == "<p>Exposé</p>"

    def test_admin_adds_amendement_for_an_organization(
        app,
        driver,
        lecture_seance_ccfp_url,
        articles_seance_ccfp,
        user_admin,
        org_gouvernement,
        org_cgt,
    ):
        from zam_repondeur.models import DBSession, Amendement, Chambre

        DBSession.add(user_admin)
        assert user_admin.membership_of(Chambre.CCFP) is None

        driver.login(user_admin.email)
        driver.get(f"{lecture_seance_ccfp_url}/amendements/saisie")
        subdiv = Select(driver.find_element_by_css_selector('select[name="subdiv"]'))
        subdiv.select_by_visible_text("Art. 2")

        organisation = Select(
            driver.find_element_by_css_selector('select[name="organisation"]')
        )
        organisation.select_by_visible_text("CGT")

        driver.switch_to.frame("corps_ifr")
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-id="corps"]',))
        ).send_keys("Corps")

        driver.switch_to.default_content()  # Required to switch to a new iframe.

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
            assert amendement.num == "CGT 1"
            assert amendement.groupe == "CGT"
            assert amendement.article.num == "2"
            assert amendement.corps == "<p>Corps</p>"
            assert amendement.expose == "<p>Exposé</p>"
