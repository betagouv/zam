import transaction


def test_amendements_not_identiques(wsgi_server, browser, lecture_an, amendements_an):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    browser.get(f"{LECTURE_URL}/amendements")
    identiques = browser.find_elements_by_css_selector("tbody tr td.identique")
    assert len(identiques) == 0


def test_amendements_identiques(wsgi_server, browser, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    with transaction.manager:
        amendements_an[0].id_identique = 42
        amendements_an[1].id_identique = 42
        DBSession.add_all(amendements_an)

    browser.get(f"{LECTURE_URL}/amendements")
    identiques = browser.find_elements_by_css_selector("tbody tr td.identique")
    assert len(identiques) == 2
    assert "first" in identiques[0].get_attribute("class")
    assert "last" not in identiques[0].get_attribute("class")
    assert "first" not in identiques[1].get_attribute("class")
    assert "last" in identiques[1].get_attribute("class")
