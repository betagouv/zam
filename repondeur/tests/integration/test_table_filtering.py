import pytest
import transaction
from selenium.webdriver.common.keys import Keys

from .helpers import extract_item_text


def test_filters_are_hidden_by_default(
    wsgi_server,
    driver,
    lecture_an,
    amendements_an,
    lecture_an_url,
    user_david,
    user_david_table_an,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendements_an[0])

    driver.get(f"{lecture_an_url}/tables/{user_david.email}")
    thead = driver.find_element_by_css_selector("thead")
    assert not thead.find_element_by_css_selector("tr.filters").is_displayed()


def test_filters_are_opened_by_click(
    wsgi_server,
    driver,
    lecture_an,
    amendements_an,
    lecture_an_url,
    user_david,
    user_david_table_an,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendements_an[0])

    driver.get(f"{lecture_an_url}/tables/{user_david.email}")
    driver.find_element_by_link_text("Filtrer").click()
    thead = driver.find_element_by_css_selector("thead")
    assert thead.find_element_by_css_selector("tr.filters").is_displayed()


def test_filters_are_absent_without_amendements(
    wsgi_server, driver, lecture_an_url, user_david
):
    driver.get(f"{lecture_an_url}/tables/{user_david.email}")
    assert not driver.find_element_by_css_selector("thead tr.filters").is_displayed()


@pytest.mark.parametrize(
    "column_index,selector,input_text,kind,initial,filtered",
    [
        (
            "1",
            ".article",
            "1",
            "article",
            ["Article 1", "Article 1", "Article 7 bis"],
            ["Article 1", "Article 1"],
        ),
        (
            "1",
            ".article",
            "7",
            "article",
            ["Article 1", "Article 1", "Article 7 bis"],
            [],
        ),
        (
            "1",
            ".article",
            "7 b",
            "article",
            ["Article 1", "Article 1", "Article 7 bis"],
            ["Article 7 bis"],
        ),
        (
            "1",
            ".article",
            "7 bis",
            "article",
            ["Article 1", "Article 1", "Article 7 bis"],
            ["Article 7 bis"],
        ),
        ("2", ".numero", "777", "amendement", ["666", "999", "777"], ["777"]),
    ],
)
def test_column_filtering_by_value(
    wsgi_server,
    driver,
    lecture_an,
    lecture_an_url,
    article7bis_an,
    amendements_an,
    user_david,
    user_david_table_an,
    column_index,
    selector,
    input_text,
    kind,
    initial,
    filtered,
):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        DBSession.add_all(amendements_an)
        user_david_table_an.amendements.append(amendements_an[0])
        user_david_table_an.amendements.append(amendements_an[1])
        amendement = Amendement.create(
            lecture=lecture_an, article=article7bis_an, num=777
        )
        user_david_table_an.amendements.append(amendement)

    driver.get(f"{lecture_an_url}/tables/{user_david.email}")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_item_text(selector, trs) == initial
    driver.find_element_by_link_text("Filtrer").click()
    input_field = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) input"
    )
    input_field.send_keys(input_text)
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_item_text(selector, trs) == filtered
    assert driver.current_url == (
        f"{lecture_an_url}/tables/{user_david.email}"
        f"?{kind}={input_text.replace(' ', '+')}"
    )
    # Restore initial state.
    input_field.send_keys(Keys.BACKSPACE * len(input_text))
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_item_text(selector, trs) == initial


@pytest.mark.parametrize(
    "column_index,selector,input_text,kind,initial,filtered",
    [
        (
            "1",
            ".article",
            "1",
            "article",
            ["Article 1", "Article 7 bis"],
            ["Article 1"],
        ),
        ("2", ".numero", "666", "amendement", ["666 et 999", "777"], ["666 et 999"]),
        ("2", ".numero", "999", "amendement", ["666 et 999", "777"], ["666 et 999"]),
        ("2", ".numero", "777", "amendement", ["666 et 999", "777"], ["777"]),
    ],
)
def test_column_filtering_by_value_with_batches(
    wsgi_server,
    driver,
    lecture_an,
    lecture_an_url,
    article7bis_an,
    amendements_an,
    user_david_table_an,
    user_david,
    column_index,
    selector,
    input_text,
    kind,
    initial,
    filtered,
):
    from zam_repondeur.models import Amendement, Batch, DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        DBSession.add_all(amendements_an)

        batch = Batch.create()
        amendements_an[0].batch = batch
        amendements_an[1].batch = batch

        user_david_table_an.amendements.append(amendements_an[0])
        user_david_table_an.amendements.append(amendements_an[1])
        amendement = Amendement.create(
            lecture=lecture_an, article=article7bis_an, num=777
        )
        user_david_table_an.amendements.append(amendement)

    driver.get(f"{lecture_an_url}/tables/{user_david.email}")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_item_text(selector, trs) == initial
    driver.find_element_by_link_text("Filtrer").click()
    input_field = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) input"
    )
    input_field.send_keys(input_text)
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_item_text(selector, trs) == filtered
    assert (
        driver.current_url
        == f"{lecture_an_url}/tables/{user_david.email}?{kind}={input_text}"
    )
    # Restore initial state.
    input_field.send_keys(Keys.BACKSPACE * len(input_text))
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_item_text(selector, trs) == initial


@pytest.mark.parametrize(
    "column_index,selector,kind,initial,filtered",
    [("2", ".numero", "gouvernemental", ["666", "999", "777"], ["777"])],
)
def test_column_filtering_by_checkbox(
    wsgi_server,
    driver,
    lecture_an,
    lecture_an_url,
    article7bis_an,
    amendements_an,
    user_david_table_an,
    user_david,
    column_index,
    selector,
    kind,
    initial,
    filtered,
):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        DBSession.add_all(amendements_an)

        user_david_table_an.amendements.append(amendements_an[0])
        user_david_table_an.amendements.append(amendements_an[1])
        amendement = Amendement.create(
            lecture=lecture_an,
            article=article7bis_an,
            num=777,
            auteur="LE GOUVERNEMENT",
        )
        user_david_table_an.amendements.append(amendement)

    driver.get(f"{lecture_an_url}/tables/{user_david.email}")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_item_text(selector, trs) == initial
    driver.find_element_by_link_text("Filtrer").click()
    label = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) label[for='{kind}']"
    )
    label.click()
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_item_text(selector, trs) == filtered
    assert driver.current_url == f"{lecture_an_url}/tables/{user_david.email}?{kind}=1"

    # Restore initial state.
    label.click()
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_item_text(selector, trs) == initial
    assert driver.current_url == f"{lecture_an_url}/tables/{user_david.email}"

    # Check filters are active on URL (re)load.
    driver.get(f"{lecture_an_url}/tables/{user_david.email}?{kind}=1")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_item_text(selector, trs) == filtered
    label = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) label[for='{kind}']"
    )
    label.click()
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_item_text(selector, trs) == initial
    assert driver.current_url == f"{lecture_an_url}/tables/{user_david.email}"
