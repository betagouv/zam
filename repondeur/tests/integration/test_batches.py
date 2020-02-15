import transaction


def test_create_batch_from_table(
    wsgi_server,
    driver,
    lecture_an,
    amendements_an,
    lecture_an_url,
    user_david,
    user_david_table_an,
):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendements_an[0])
        user_david_table_an.add_amendement(amendements_an[1])

    driver.get(f"{lecture_an_url}/tables/{user_david.email}/")
    checkboxes = driver.find_elements_by_css_selector('[name="amendement-selected"]')
    checkboxes[0].click()
    checkboxes[1].click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert group_actions.is_displayed()
    batch_amendements = driver.find_element_by_css_selector("#batch-amendements")
    assert batch_amendements.is_displayed()
    batch_amendements.click()
    assert driver.current_url == f"{lecture_an_url}/batch_amendements?n=666&n=999"
    submit_button = driver.find_element_by_css_selector(
        '#batch-amendements input[type="submit"]'
    )
    submit_button.click()
    assert driver.current_url == f"{lecture_an_url}/tables/{user_david.email}/"

    with transaction.manager:
        amendements = DBSession.query(Amendement).all()
        assert amendements[0].location.batch.pk == amendements[1].location.batch.pk == 1


def test_dissociate_batch_from_amendement_edit(
    wsgi_server,
    driver,
    lecture_an,
    amendements_an_batch,
    lecture_an_url,
    user_david,
    user_david_table_an,
):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendements_an_batch[0])
        user_david_table_an.add_amendement(amendements_an_batch[1])

    driver.get(
        f"{lecture_an_url}/amendements/{amendements_an_batch[0]}/amendement_edit"
    )
    dissociate_button = driver.find_element_by_css_selector('[value="Retirer du lot"]')
    dissociate_button.click()
    assert driver.current_url == f"{lecture_an_url}/tables/{user_david.email}/"

    with transaction.manager:
        amendements = DBSession.query(Amendement).all()
        assert amendements[0].location.batch is None
        assert amendements[1].location.batch is None


def test_transfer_batch_from_table(
    wsgi_server,
    driver,
    lecture_an,
    amendements_an_batch,
    lecture_an_url,
    user_david,
    user_david_table_an,
):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendements_an_batch[0])
        user_david_table_an.add_amendement(amendements_an_batch[0])

    driver.get(f"{lecture_an_url}/tables/{user_david.email}/")
    checkbox = driver.find_element_by_css_selector('[name="amendement-selected"]')
    checkbox.click()
    group_actions = driver.find_element_by_css_selector(".groupActions")
    assert group_actions.is_displayed()
    transfer_amendements = driver.find_element_by_css_selector("#transfer-amendements")
    assert transfer_amendements.is_displayed()
    transfer_amendements.click()
    assert driver.current_url == (
        f"{lecture_an_url}/transfer_amendements?n=666"
        f"&back=%2Fdossiers%2F{lecture_an.dossier.url_key}"
        "%2Flectures%2Fan.15.269.PO717460%2Ftables%2Fdavid%40exemple.gouv.fr%2F"
    )
    submit_button = driver.find_element_by_css_selector('input[name="submit-index"]')
    submit_button.click()
    assert driver.current_url == f"{lecture_an_url}/tables/{user_david.email}/"

    with transaction.manager:
        user = DBSession.query(User).filter(User.email == user_david.email).first()
        table = user.table_for(lecture_an)
        assert table.amendements == []
