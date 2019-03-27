import transaction


def test_amendements_not_identiques(wsgi_server, driver, lecture_an, amendements_an):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    identiques = driver.find_elements_by_css_selector("tbody tr td.identique")
    assert len(identiques) == 0


def test_amendements_identiques(wsgi_server, driver, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    with transaction.manager:
        amendements_an[0].id_identique = 42
        amendements_an[1].id_identique = 42
        DBSession.add_all(amendements_an)

    driver.get(f"{LECTURE_URL}/amendements")
    identiques = driver.find_elements_by_css_selector("tbody tr td.identique")
    assert len(identiques) == 2
    assert "first" in identiques[0].get_attribute("class")
    assert "last" not in identiques[0].get_attribute("class")
    assert "first" not in identiques[1].get_attribute("class")
    assert "last" in identiques[1].get_attribute("class")


def test_amendements_identiques_with_abandoned(
    wsgi_server, driver, lecture_an, amendements_an, article1_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add_all(amendements_an)

        amendements_an[0].id_identique = 42
        amendements_an[1].id_identique = 42
        assert amendements_an[0].all_identiques == [amendements_an[1]]
        assert amendements_an[1].all_identiques == [amendements_an[0]]

        amendements_an[1].sort = "retiré"
        assert amendements_an[1].is_abandoned
        assert amendements_an[0].all_identiques == []
        assert amendements_an[1].all_identiques == [amendements_an[0]]

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")

    amendements = driver.find_elements_by_css_selector("tbody tr")
    assert len(amendements) == 2

    identiques = driver.find_elements_by_css_selector("tbody tr td.identique")
    assert len(identiques) == 0
