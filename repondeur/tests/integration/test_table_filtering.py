import pytest
import transaction
from selenium.webdriver.common.keys import Keys

from .helpers import extract_item_text


def test_filters_are_hidden_by_default(wsgi_server, driver, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession, User

    email = "user@example.com"
    with transaction.manager:
        user = DBSession.query(User).filter(User.email == email).first()
        table = user.table_for(lecture_an)
        table.amendements.append(amendements_an[0])

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/tables/{email}")
    thead = driver.find_element_by_css_selector("thead")
    assert not thead.find_element_by_css_selector("tr.filters").is_displayed()


def test_filters_are_opened_by_click(wsgi_server, driver, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession, User

    email = "user@example.com"
    with transaction.manager:
        user = DBSession.query(User).filter(User.email == email).first()
        table = user.table_for(lecture_an)
        table.amendements.append(amendements_an[0])

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/tables/{email}")
    driver.find_element_by_link_text("Filtrer").click()
    thead = driver.find_element_by_css_selector("thead")
    assert thead.find_element_by_css_selector("tr.filters").is_displayed()


def test_filters_are_absent_without_amendements(
    wsgi_server, driver, lecture_an, user_david
):
    email = "user@example.com"
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    driver.get(f"{LECTURE_URL}/tables/{email}")
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
        ("2", ".numero", "777", "amendement", ["666", "999", "777"], ["777"]),
    ],
)
def test_column_filtering_by(
    wsgi_server,
    driver,
    lecture_an,
    article7bis_an,
    amendements_an,
    column_index,
    selector,
    input_text,
    kind,
    initial,
    filtered,
):
    from zam_repondeur.models import Amendement, DBSession, User

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    email = "user@example.com"
    with transaction.manager:
        DBSession.add_all(amendements_an)
        user = DBSession.query(User).filter(User.email == email).first()
        table = user.table_for(lecture_an)
        table.amendements.append(amendements_an[0])
        table.amendements.append(amendements_an[1])
        amendement = Amendement.create(
            lecture=lecture_an, article=article7bis_an, num=777
        )
        table.amendements.append(amendement)

    driver.get(f"{LECTURE_URL}/tables/{email}")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_item_text(selector, trs) == initial
    driver.find_element_by_link_text("Filtrer").click()
    input_field = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) input"
    )
    input_field.send_keys(input_text)
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_item_text(selector, trs) == filtered
    assert driver.current_url == f"{LECTURE_URL}/tables/{email}?{kind}={input_text}"
    # Restore initial state.
    input_field.send_keys(Keys.BACKSPACE * len(input_text))
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_item_text(selector, trs) == initial
