import transaction

import pytest
from selenium.webdriver.common.keys import Keys

from .helpers import extract_column_text


def test_filters_are_visible_by_default(
    wsgi_server, driver, lecture_an, amendements_an
):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    thead = driver.find_element_by_css_selector("thead")
    assert thead.find_element_by_css_selector("tr.filters").is_displayed()


def test_filters_are_ineffective_without_amendements(wsgi_server, driver, lecture_an):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/amendements")
    thead = driver.find_element_by_css_selector("thead")
    assert not thead.find_element_by_css_selector("tr.filters").is_displayed()


@pytest.mark.parametrize(
    "column_index,input_text,kind,initial,filtered",
    [
        ("2", "1", "article", ["Art. 1", "Art. 1", "Art. 7 bis"], ["Art. 1", "Art. 1"]),
        ("2", "7", "article", ["Art. 1", "Art. 1", "Art. 7 bis"], []),
        ("2", "7 b", "article", ["Art. 1", "Art. 1", "Art. 7 bis"], ["Art. 7 bis"]),
        ("2", "7 bis", "article", ["Art. 1", "Art. 1", "Art. 7 bis"], ["Art. 7 bis"]),
        ("3", "777", "amendement", ["666", "999", "777"], ["777"]),
        ("4", "Da", "table", ["Ronan", "David", "Daniel"], ["David", "Daniel"]),
    ],
)
def test_column_filtering_by_value(
    wsgi_server,
    driver,
    lecture_an,
    article7bis_an,
    amendements_an,
    user_david_table_an,
    user_ronan_table_an,
    user_daniel_table_an,
    column_index,
    input_text,
    kind,
    initial,
    filtered,
):
    from zam_repondeur.models import Amendement, DBSession

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    with transaction.manager:
        DBSession.add(user_ronan_table_an)
        DBSession.add(user_david_table_an)
        DBSession.add(user_daniel_table_an)

        user_ronan_table_an.amendements.append(amendements_an[0])
        user_david_table_an.amendements.append(amendements_an[1])
        amendement = Amendement.create(
            lecture=lecture_an, article=article7bis_an, num=777
        )
        user_daniel_table_an.amendements.append(amendement)

    driver.get(f"{LECTURE_URL}/amendements")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    input_field = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) input"
    )
    input_field.send_keys(input_text)
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == filtered
    assert (
        driver.current_url
        == f"{LECTURE_URL}/amendements?{kind}={input_text.replace(' ', '+')}"
    )

    # Restore initial state.
    input_field.send_keys(Keys.BACKSPACE * len(input_text))
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    assert driver.current_url == f"{LECTURE_URL}/amendements"

    # Check filters are active on URL (re)load.
    driver.get(f"{LECTURE_URL}/amendements?{kind}={input_text}")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == filtered
    input_field = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) input"
    )
    input_field.send_keys(Keys.BACKSPACE * len(input_text))
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    assert driver.current_url == f"{LECTURE_URL}/amendements"


@pytest.mark.parametrize(
    "column_index,input_text,kind,initial,filtered",
    [
        ("2", "1", "article", ["Art. 1", "Art. 7 bis"], ["Art. 1"]),
        ("3", "666", "amendement", ["666, 999", "777"], ["666, 999"]),
        ("3", "999", "amendement", ["666, 999", "777"], ["666, 999"]),
        ("3", "777", "amendement", ["666, 999", "777"], ["777"]),
    ],
)
def test_column_filtering_by_value_with_batches(
    wsgi_server,
    driver,
    lecture_an,
    article7bis_an,
    amendements_an,
    user_david_table_an,
    user_ronan_table_an,
    user_daniel_table_an,
    column_index,
    input_text,
    kind,
    initial,
    filtered,
):
    from zam_repondeur.models import Amendement, Batch, DBSession

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    with transaction.manager:
        DBSession.add(user_ronan_table_an)
        DBSession.add(user_david_table_an)
        DBSession.add(user_daniel_table_an)

        batch = Batch.create()
        amendements_an[0].batch = batch
        amendements_an[1].batch = batch

        user_ronan_table_an.amendements.append(amendements_an[0])
        user_david_table_an.amendements.append(amendements_an[1])
        amendement = Amendement.create(
            lecture=lecture_an, article=article7bis_an, num=777
        )
        user_daniel_table_an.amendements.append(amendement)

    driver.get(f"{LECTURE_URL}/amendements")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
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
    assert driver.current_url == f"{LECTURE_URL}/amendements"

    # Check filters are active on URL (re)load.
    driver.get(f"{LECTURE_URL}/amendements?{kind}={input_text}")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == filtered
    input_field = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) input"
    )
    input_field.send_keys(Keys.BACKSPACE * len(input_text))
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    assert driver.current_url == f"{LECTURE_URL}/amendements"


@pytest.mark.parametrize(
    "column_index,kind,initial,filtered",
    [
        ("3", "gouvernemental", ["666", "999", "777 Gouv."], ["777 Gouv."]),
        ("4", "emptytable", ["", "", "David"], ["", ""]),
    ],
)
def test_column_filtering_by_checkbox(
    wsgi_server,
    driver,
    lecture_an,
    article7bis_an,
    amendements_an,
    user_david_table_an,
    column_index,
    kind,
    initial,
    filtered,
):
    from zam_repondeur.models import Amendement, DBSession

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    with transaction.manager:
        DBSession.add(user_david_table_an)
        amendement = Amendement.create(
            lecture=lecture_an,
            article=article7bis_an,
            num=777,
            auteur="LE GOUVERNEMENT",
        )
        user_david_table_an.amendements.append(amendement)

    driver.get(f"{LECTURE_URL}/amendements")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    label = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) label[for='{kind}']"
    )
    label.click()
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == filtered
    assert driver.current_url == f"{LECTURE_URL}/amendements?{kind}=1"

    # Restore initial state.
    label.click()
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    assert driver.current_url == f"{LECTURE_URL}/amendements"

    # Check filters are active on URL (re)load.
    driver.get(f"{LECTURE_URL}/amendements?{kind}=1")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == filtered
    label = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) label[for='{kind}']"
    )
    label.click()
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    assert driver.current_url == f"{LECTURE_URL}/amendements"


@pytest.mark.parametrize(
    "column_index,input_text,kind,initial,filtered",
    [
        (
            "3",
            "act",
            "mission",
            ["Action transfo.", "Action transfo.", "Action ext."],
            ["Action transfo.", "Action transfo.", "Action ext."],
        ),
        (
            "3",
            "action e",
            "mission",
            ["Action transfo.", "Action transfo.", "Action ext."],
            ["Action ext."],
        ),
        # Check other filters are still working.
        ("2", "1", "article", ["Art. 1", "Art. 1", "Art. 7 bis"], ["Art. 1", "Art. 1"]),
        ("4", "222", "amendement", ["111", "333", "222"], ["222"]),
    ],
)
def test_column_filtering_by_value_for_missions(
    wsgi_server,
    driver,
    lecture_plf2018_an_premiere_lecture_seance_publique_2,
    article7bis_an,
    amendements_plf2018_an_premiere_lecture_seance_publique_2,
    column_index,
    input_text,
    kind,
    initial,
    filtered,
):
    from zam_repondeur.models import Amendement, AmendementMission, DBSession

    LECTURE_URL = (
        f"{wsgi_server.application_url}lectures/"
        f"{lecture_plf2018_an_premiere_lecture_seance_publique_2.url_key}"
    )
    with transaction.manager:
        amendement = Amendement.create(
            lecture=lecture_plf2018_an_premiere_lecture_seance_publique_2,
            article=article7bis_an,
            num=222,
        )
        AmendementMission.create(
            amendement,
            titre="Mission Action extérieure de l'État",
            titre_court="Action ext.",
        )
        DBSession.add(amendement)

    driver.get(f"{LECTURE_URL}/amendements")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    input_field = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) input"
    )
    input_field.send_keys(input_text)
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == filtered
    assert (
        driver.current_url
        == f"{LECTURE_URL}/amendements?{kind}={input_text.replace(' ', '+')}"
    )

    # Restore initial state.
    input_field.send_keys(Keys.BACKSPACE * len(input_text))
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    assert driver.current_url == f"{LECTURE_URL}/amendements"

    # Check filters are active on URL (re)load.
    driver.get(f"{LECTURE_URL}/amendements?{kind}={input_text}")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == filtered
    input_field = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) input"
    )
    input_field.send_keys(Keys.BACKSPACE * len(input_text))
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    assert driver.current_url == f"{LECTURE_URL}/amendements"
