import transaction

import pytest

from .helpers import extract_column_text, find_header_by_index


def test_column_sorting_once_changes_url(wsgi_server, driver, lecture_an):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    article_header = find_header_by_index(
        1, driver.find_element_by_css_selector("thead")
    )
    article_header.click()
    assert driver.current_url == f"{LECTURE_URL}/amendements?sort=1asc"


def test_column_sorting_twice_changes_url_direction(wsgi_server, driver, lecture_an):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    article_header = find_header_by_index(
        1, driver.find_element_by_css_selector("thead")
    )
    article_header.click()
    article_header.click()
    assert driver.current_url == f"{LECTURE_URL}/amendements?sort=1desc"


def test_column_sorting_thrice_changes_url_again(wsgi_server, driver, lecture_an):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    article_header = find_header_by_index(
        1, driver.find_element_by_css_selector("thead")
    )
    article_header.click()
    article_header.click()
    article_header.click()
    assert driver.current_url == f"{LECTURE_URL}/amendements?sort=1asc"


def test_column_sorting_is_cancelable(wsgi_server, driver, lecture_an):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    article_header = find_header_by_index(
        1, driver.find_element_by_css_selector("thead")
    )
    article_header.click()
    assert driver.current_url == f"{LECTURE_URL}/amendements?sort=1asc"
    cancel = driver.find_element_by_css_selector("#unsort")
    cancel.click()
    assert driver.current_url == f"{LECTURE_URL}/amendements"


def test_column_sorting_multiple_changes_url(wsgi_server, driver, lecture_an):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    find_header_by_index(1, driver.find_element_by_css_selector("thead")).click()
    find_header_by_index(2, driver.find_element_by_css_selector("thead")).click()
    assert driver.current_url == f"{LECTURE_URL}/amendements?sort=1asc-2asc"
    # Still cancelable
    driver.find_element_by_css_selector("#unsort").click()
    assert driver.current_url == f"{LECTURE_URL}/amendements"


@pytest.mark.parametrize(
    "column_index,kind,initial_order,asc_order",
    [
        (
            "1",
            "article",
            ["Art. 1", "Art. 1", "Avant art. 1"],
            ["Avant art. 1", "Art. 1", "Art. 1"],
        ),
        ("2", "amendement", ["666", "999", "777"], ["666", "777", "999"]),
        ("3", "table", ["Ronan", "David", "Daniel"], ["Daniel", "David", "Ronan"]),
        ("4", "avis", ["#check", "", "#check"], ["", "#check", "#check"]),
        ("5", "reponse", ["#check", "", "#check"], ["#check", "#check", ""]),
    ],
)
def test_column_sorting_by(
    wsgi_server,
    driver,
    lecture_an,
    article1av_an,
    amendements_an,
    user_david,
    user_ronan,
    user_daniel,
    column_index,
    kind,
    initial_order,
    asc_order,
):
    from zam_repondeur.models import Amendement, DBSession

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    with transaction.manager:
        DBSession.add_all(amendements_an)

        amendements_an[0].user_content.avis = "Défavorable"
        amendements_an[0].user_content.reponse = "Foo"
        user_ronan.table.amendements.append(amendements_an[0])

        user_david.table.amendements.append(amendements_an[1])

        amendement = Amendement.create(
            lecture=lecture_an,
            article=article1av_an,
            num=777,
            avis="Favorable",
            reponse="Baz",
        )
        user_daniel.table.amendements.append(amendement)

    driver.get(f"{LECTURE_URL}/amendements")
    trs = driver.find_elements_by_css_selector("tbody tr")
    assert extract_column_text(column_index, trs) == initial_order
    find_header_by_index(
        column_index, driver.find_element_by_css_selector("thead")
    ).click()
    trs = driver.find_elements_by_css_selector("tbody tr")
    assert extract_column_text(column_index, trs) == asc_order
    assert driver.current_url == f"{LECTURE_URL}/amendements?sort={column_index}asc"
    find_header_by_index(
        column_index, driver.find_element_by_css_selector("thead")
    ).click()
    trs = driver.find_elements_by_css_selector("tbody tr")
    assert extract_column_text(column_index, trs) == list(reversed(asc_order))
    assert driver.current_url == f"{LECTURE_URL}/amendements?sort={column_index}desc"
    # Cancel sort.
    cancel = driver.find_element_by_css_selector("#unsort")
    cancel.click()
    trs = driver.find_elements_by_css_selector("tbody tr")
    assert extract_column_text(column_index, trs) == initial_order
    assert driver.current_url == f"{LECTURE_URL}/amendements"
