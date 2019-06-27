import time

import transaction
from selenium.webdriver.support.ui import Select


def test_amendement_edition_start_editing_status(
    wsgi_server, driver, lecture_an, amendements_an
):
    from zam_repondeur.models import DBSession, User

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    amendement = amendements_an[0]
    with transaction.manager:
        user = (
            DBSession.query(User).filter(User.email == "user@exemple.gouv.fr").first()
        )
        table = user.table_for(lecture_an)
        DBSession.add(table)
        table.amendements.append(amendement)
        DBSession.add(amendement)

    assert not amendement.is_being_edited

    driver.get(f"{LECTURE_URL}/amendements/{amendements_an[0].num}/amendement_edit")
    avis = Select(driver.find_element_by_css_selector('select[name="avis"]'))
    avis.select_by_visible_text("Défavorable")
    time.sleep(1)  # Wait for the option to be selected.

    assert amendement.is_being_edited


def test_amendement_edition_exit_stop_editing_status(
    wsgi_server, driver, lecture_an, amendements_an
):
    from zam_repondeur.models import DBSession, User

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    amendement = amendements_an[0]
    with transaction.manager:
        user = (
            DBSession.query(User).filter(User.email == "user@exemple.gouv.fr").first()
        )
        table = user.table_for(lecture_an)
        DBSession.add(table)
        table.amendements.append(amendement)
        DBSession.add(amendement)

    assert not amendement.is_being_edited

    driver.get(f"{LECTURE_URL}/amendements/{amendements_an[0].num}/amendement_edit")
    avis = Select(driver.find_element_by_css_selector('select[name="avis"]'))
    avis.select_by_visible_text("Défavorable")
    time.sleep(1)  # Wait for the option to be selected.

    assert amendement.is_being_edited

    exit_link = driver.find_element_by_css_selector(".save-buttons a.arrow-left")
    exit_link.click()
    driver.switch_to.alert.accept()
    time.sleep(1)  # Wait for the alert to actually redirect.

    assert not amendement.is_being_edited
