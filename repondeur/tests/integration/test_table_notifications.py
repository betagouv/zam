from time import sleep

import pytest
import transaction

pytestmark = pytest.mark.flaky(max_runs=5)


def test_table_notification_on_amendement_transfer(
    wsgi_server, driver, lecture_an_url, amendements_an, user_david_table_an, user_david
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendements_an[0])
        DBSession.add_all(amendements_an)

    driver.get(f"{lecture_an_url}/tables/{user_david.email}")
    status = driver.find_element_by_css_selector('div[role="status"] div')
    assert not status.is_displayed()
    assert not status.text

    with transaction.manager:
        amendements_an[0].user_table = None
        DBSession.add_all(amendements_an)

    sleep(wsgi_server.settings["zam.check_for.transfers_from_to_my_table"])

    assert status.is_displayed()
    assert status.text == "L’amendement 666 a été retiré de votre table. Rafraîchir"
