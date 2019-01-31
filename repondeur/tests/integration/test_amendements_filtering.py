import transaction

import pytest
from selenium.webdriver.common.keys import Keys

from .helpers import extract_column_text


def test_filters_are_hidden_by_default(wsgi_server, driver, lecture_an):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    thead = driver.find_element_by_css_selector("thead")
    assert not thead.find_element_by_css_selector("tr:nth-child(2)").is_displayed()


def test_filters_are_opened_by_click(wsgi_server, driver, lecture_an):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    driver.find_element_by_link_text("Filtrer").click()
    thead = driver.find_element_by_css_selector("thead")
    assert thead.find_element_by_css_selector("tr:nth-child(2)").is_displayed()


@pytest.mark.parametrize(
    "column_index,input_text,kind,initial,filtered",
    [
        ("1", "1", "article", ["Art. 1", "Art. 1", "Art. 7 bis"], ["Art. 1", "Art. 1"]),
        ("2", "777", "amendement", ["666", "999", "777"], ["777"]),
        ("5", "Da", "status", ["Ronan", "David", "Daniel"], ["David", "Daniel"]),
    ],
)
def test_column_filtering_by(
    wsgi_server,
    driver,
    lecture_an,
    article7bis_an,
    amendements_an,
    user_david,
    user_ronan,
    user_daniel,
    column_index,
    input_text,
    kind,
    initial,
    filtered,
):
    from zam_repondeur.models import Amendement, DBSession

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    with transaction.manager:
        amendements_an[0].user_space.user = user_ronan
        amendements_an[1].user_space.user = user_david
        amendement = Amendement.create(
            lecture=lecture_an, article=article7bis_an, num=777
        )
        amendement.user_space.user = user_daniel
        DBSession.add_all(amendements_an)

    driver.get(f"{LECTURE_URL}/amendements")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    driver.find_element_by_link_text("Filtrer").click()
    input_field = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) input"
    )
    input_field.send_keys(input_text)
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == filtered
    assert driver.current_url == f"{LECTURE_URL}/amendements?{kind}={input_text}"
    # Restore initial state.
    input_field.send_keys(Keys.BACKSPACE * len(input_text))
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
