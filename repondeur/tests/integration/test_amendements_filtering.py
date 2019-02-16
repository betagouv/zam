import transaction

import pytest
from selenium.webdriver.common.keys import Keys

from .helpers import extract_column_text


def test_filters_are_hidden_by_default(wsgi_server, driver, lecture_an):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    thead = driver.find_element_by_css_selector("thead")
    assert not thead.find_element_by_css_selector("tr.filters").is_displayed()


def test_filters_are_opened_by_click(wsgi_server, driver, lecture_an):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    driver.find_element_by_link_text("Filtrer").click()
    thead = driver.find_element_by_css_selector("thead")
    assert thead.find_element_by_css_selector("tr.filters").is_displayed()


@pytest.mark.parametrize(
    "column_index,input_text,kind,initial,filtered",
    [
        ("2", "1", "article", ["Art. 1", "Art. 1", "Art. 7 bis"], ["Art. 1", "Art. 1"]),
        ("3", "777", "amendement", ["666", "999", "777"], ["777"]),
        ("4", "Da", "table", ["Ronan", "David", "Daniel"], ["David", "Daniel"]),
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
        DBSession.add_all(amendements_an)
        table_ronan = user_ronan.table_for(lecture_an)
        table_ronan.amendements.append(amendements_an[0])
        table_david = user_david.table_for(lecture_an)
        table_david.amendements.append(amendements_an[1])
        amendement = Amendement.create(
            lecture=lecture_an, article=article7bis_an, num=777
        )
        table_daniel = user_daniel.table_for(lecture_an)
        table_daniel.amendements.append(amendement)

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
