from time import sleep

import pytest
import transaction

pytestmark = pytest.mark.flaky(max_runs=5)


def test_amendement_edit_notification_on_amendement_transfer(
    wsgi_server, driver, lecture_an, amendements_an, lecture_an_url, user_david_table_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendements_an[0])
        DBSession.add_all(amendements_an)

    driver.get(f"{lecture_an_url}/amendements/{amendements_an[0].num}/amendement_edit")
    status = driver.find_element_by_css_selector('div[role="status"] div')
    assert not status.is_displayed()
    assert not status.text

    with transaction.manager:
        amendements_an[0].user_table = None
        DBSession.add_all(amendements_an)

    sleep(wsgi_server.settings["zam.check_for.amendement_stolen_while_editing"])

    assert status.is_displayed()
    assert status.text == (
        "L’amendement en cours d’édition n’est plus sur votre table. "
        "Votre saisie ne va PAS être sauvegardée. Retourner à ma table"
    )
