import pytest
import transaction
from datetime import datetime
from time import sleep


pytestmark = pytest.mark.flaky(max_runs=5)


def test_amendements_index_notification_on_amendement_update(
    wsgi_server, driver, lecture_an, amendements_an
):
    from zam_repondeur.models import DBSession

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    with transaction.manager:
        amendements_an[0].user_content.avis = "Favorable"
        amendements_an[0].auteur = "M. Content"
        amendements_an[0].groupe = "Les Heureux"
        DBSession.add_all(amendements_an)

    driver.get(f"{LECTURE_URL}/amendements")
    status = driver.find_element_by_css_selector('div[role="status"] div')
    assert not status.is_displayed()
    assert not status.text

    with transaction.manager:
        amendements_an[0].user_content.avis = "Défavorable"
        amendements_an[0].modified_at = datetime.utcnow()
        DBSession.add_all(amendements_an)

    sleep(wsgi_server.settings["zam.check.on_updates_for_the_index"])

    assert status.is_displayed()
    assert status.text == "L’amendement 666 a été mis à jour ! Rafraîchir"
