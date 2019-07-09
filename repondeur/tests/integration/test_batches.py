import transaction


def test_create_batch_from_table(wsgi_server, driver, lecture_an, amendements_an):
    from zam_repondeur.models import Amendement, DBSession, User

    email = "user@exemple.gouv.fr"
    with transaction.manager:
        user = DBSession.query(User).filter(User.email == email).first()
        table = user.table_for(lecture_an)
        table.amendements.append(amendements_an[0])
        table.amendements.append(amendements_an[1])

    LECTURE_URL = f"{wsgi_server.application_url}{lecture_an.url}"
    driver.get(f"{LECTURE_URL}/tables/{email}")
    checkboxes = driver.find_elements_by_css_selector('[name="amendement-selected"]')
    checkboxes[0].click()
    checkboxes[1].click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert group_actions.is_displayed()
    batch_amendements = driver.find_element_by_css_selector("#batch-amendements")
    assert batch_amendements.is_displayed()
    batch_amendements.click()
    assert driver.current_url == f"{LECTURE_URL}/batch_amendements?nums=666&nums=999"
    submit_button = driver.find_element_by_css_selector('input[type="submit"]')
    submit_button.click()
    assert driver.current_url == f"{LECTURE_URL}/tables/{email}"

    with transaction.manager:
        amendements = DBSession.query(Amendement).all()
        assert amendements[0].batch.pk == amendements[1].batch.pk == 1


def test_dissociate_batch_from_amendement_edit(
    wsgi_server, driver, lecture_an, amendements_an_batch
):
    from zam_repondeur.models import Amendement, DBSession, User

    email = "user@exemple.gouv.fr"
    with transaction.manager:
        user = DBSession.query(User).filter(User.email == email).first()
        table = user.table_for(lecture_an)
        table.amendements.append(amendements_an_batch[0])
        table.amendements.append(amendements_an_batch[1])

    LECTURE_URL = f"{wsgi_server.application_url}{lecture_an.url}"
    driver.get(f"{LECTURE_URL}/{amendements_an_batch[0]}/amendement_edit")
    dissociate_button = driver.find_element_by_css_selector('[value="Retirer du lot"]')
    dissociate_button.click()
    assert driver.current_url == f"{LECTURE_URL}/tables/{email}"

    with transaction.manager:
        amendements = DBSession.query(Amendement).all()
        assert amendements[0].batch is None
        assert amendements[1].batch is None


def test_transfer_batch_from_table(
    wsgi_server, driver, lecture_an, amendements_an_batch
):
    from zam_repondeur.models import DBSession, User

    email = "user@exemple.gouv.fr"
    with transaction.manager:
        user = DBSession.query(User).filter(User.email == email).first()
        table = user.table_for(lecture_an)
        table.amendements.append(amendements_an_batch[0])
        table.amendements.append(amendements_an_batch[1])

    LECTURE_URL = f"{wsgi_server.application_url}{lecture_an.url}"
    driver.get(f"{LECTURE_URL}/tables/{email}")
    checkbox = driver.find_element_by_css_selector('[name="amendement-selected"]')
    checkbox.click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert group_actions.is_displayed()
    transfer_amendements = driver.find_element_by_css_selector("#transfer-amendements")
    assert transfer_amendements.is_displayed()
    transfer_amendements.click()
    assert driver.current_url == (
        f"{LECTURE_URL}/transfer_amendements?nums=666"
        "&back=%2Flectures%2Fan.15.269.PO717460%2Ftables%2Fuser%40exemple.gouv.fr"
    )
    submit_button = driver.find_element_by_css_selector('input[name="submit-index"]')
    submit_button.click()
    assert driver.current_url == f"{LECTURE_URL}/tables/{email}"

    with transaction.manager:
        user = DBSession.query(User).filter(User.email == email).first()
        table = user.table_for(lecture_an)
        assert table.amendements == []
