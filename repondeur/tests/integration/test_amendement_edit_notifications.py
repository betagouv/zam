import pytest
import transaction
from time import sleep


pytestmark = pytest.mark.flaky(max_runs=5)


def test_amendement_edit_notification_on_amendement_transfer(
    wsgi_server, driver, lecture_an, amendements_an
):
    from zam_repondeur.models import DBSession, User

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    with transaction.manager:
        user = (
            DBSession.query(User).filter(User.email == "user@exemple.gouv.fr").first()
        )
        table = user.table_for(lecture_an)
        DBSession.add(table)
        table.amendements.append(amendements_an[0])
        DBSession.add_all(amendements_an)

    driver.get(f"{LECTURE_URL}/amendements/{amendements_an[0].num}/amendement_edit")
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
