import pytest
import transaction
from selenium.webdriver.common.keys import Keys

from .helpers import extract_column_text


def test_filters_are_visible_by_default(
    wsgi_server, driver, lecture_an_url, amendements_an
):
    driver.get(f"{lecture_an_url}/amendements/")
    thead = driver.find_element_by_css_selector("thead")
    assert thead.find_element_by_css_selector("tr.filters").is_displayed()


def test_filters_are_always_visible(wsgi_server, driver, lecture_an_url):
    driver.get(f"{lecture_an_url}/amendements/")
    thead = driver.find_element_by_css_selector("thead")
    assert thead.find_element_by_css_selector("tr.filters").is_displayed()


def test_number_of_amendements_is_displayed(
    wsgi_server, driver, lecture_an_url, amendements_an
):
    driver.get(f"{lecture_an_url}/amendements/")
    trs = driver.find_elements_by_css_selector("tbody tr")
    assert len(trs) == 2
    counter = driver.find_element_by_css_selector(
        'span[data-target="amendements-filters.count"]'
    )
    assert counter.text == "2 amendements"


def test_number_of_amendements_is_displayed_too_many_amendements(
    wsgi_server,
    driver,
    settings,
    article1_an,
    lecture_an,
    lecture_an_url,
    amendements_an,
):
    from zam_repondeur.models import Amendement

    nb_amendements = int(settings["zam.limits.max_amendements_for_full_index"])

    with transaction.manager:
        for i in range(nb_amendements):
            Amendement.create(lecture=lecture_an, article=article1_an, num=i + 1)

    driver.get(f"{lecture_an_url}/amendements/")
    trs = driver.find_elements_by_css_selector("tbody tr")
    assert len(trs) == 7
    counter = driver.find_element_by_css_selector(
        'span[data-target="amendements-filters.count"]'
    )
    assert counter.text == "7 amendements pour cet article • 7 amendements au total"


def test_number_of_amendements_is_displayed_with_limit_derouleur(
    wsgi_server, driver, lecture_an_url, amendements_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendements_an[0].position = None
        for amendement in amendements_an:
            amendement.user_content.avis = "Favorable"
        DBSession.add_all(amendements_an)

    driver.get(f"{lecture_an_url}/amendements/")
    trs = driver.find_elements_by_css_selector("tbody tr")
    assert len(trs) == 3
    counter = driver.find_element_by_css_selector(
        'span[data-target="amendements-filters.count"]'
    )
    assert counter.text == "2 amendements"


@pytest.mark.parametrize(
    "column_index,input_text,kind,initial,filtered",
    [
        ("3", "777", "amendement", ["666", "999", "777"], ["777"]),
        ("4", "Da", "table", ["Ronan", "David", "Daniel"], ["David", "Daniel"]),
    ],
)
def test_column_filtering_by_value(
    wsgi_server,
    driver,
    lecture_an,
    lecture_an_url,
    article1_an,
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

    with transaction.manager:
        DBSession.add(user_ronan_table_an)
        DBSession.add(user_david_table_an)
        DBSession.add(user_daniel_table_an)

        user_ronan_table_an.add_amendement(amendements_an[0])
        user_david_table_an.add_amendement(amendements_an[1])
        amendement = Amendement.create(
            lecture=lecture_an, article=article1_an, num=777, position=3
        )
        user_daniel_table_an.add_amendement(amendement)

    driver.get(f"{lecture_an_url}/amendements/")
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
        == f"{lecture_an_url}/amendements/?{kind}={input_text.replace(' ', '+')}"
    )

    # Restore initial state.
    input_field.send_keys(Keys.BACKSPACE * len(input_text))
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    assert driver.current_url == f"{lecture_an_url}/amendements/"

    # Check filters are active on URL (re)load.
    driver.get(f"{lecture_an_url}/amendements/?{kind}={input_text}")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == filtered
    input_field = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) input"
    )
    input_field.send_keys(Keys.BACKSPACE * len(input_text))
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    assert driver.current_url == f"{lecture_an_url}/amendements/"


@pytest.mark.parametrize(
    "column_index,input_text,kind,initial,filtered",
    [
        ("4", "da", "table", ["David", "Test table"], ["David"]),
        ("4", "te", "table", ["David", "Test table"], ["Test table"]),
    ],
)
def test_column_filtering_by_value_with_shared_tables(
    wsgi_server,
    driver,
    lecture_an,
    lecture_an_url,
    article1_an,
    amendements_an,
    user_david_table_an,
    shared_table_lecture_an,
    column_index,
    input_text,
    kind,
    initial,
    filtered,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        DBSession.add(shared_table_lecture_an)

        user_david_table_an.add_amendement(amendements_an[0])
        shared_table_lecture_an.add_amendement(amendements_an[1])

    driver.get(f"{lecture_an_url}/amendements")
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
        == f"{lecture_an_url}/amendements?{kind}={input_text.replace(' ', '+')}"
    )

    # Restore initial state.
    input_field.send_keys(Keys.BACKSPACE * len(input_text))
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    assert driver.current_url == f"{lecture_an_url}/amendements"

    # Check filters are active on URL (re)load.
    driver.get(f"{lecture_an_url}/amendements?{kind}={input_text}")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == filtered
    input_field = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) input"
    )
    input_field.send_keys(Keys.BACKSPACE * len(input_text))
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    assert driver.current_url == f"{lecture_an_url}/amendements"


@pytest.mark.parametrize(
    "column_index,input_text,kind,initial,filtered",
    [
        ("3", "666", "amendement", ["666, 999", "777"], ["666, 999"]),
        ("3", "999", "amendement", ["666, 999", "777"], ["666, 999"]),
        ("3", "777", "amendement", ["666, 999", "777"], ["777"]),
    ],
)
def test_column_filtering_by_value_with_batches(
    wsgi_server,
    driver,
    lecture_an,
    lecture_an_url,
    article1_an,
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

    with transaction.manager:
        DBSession.add(user_ronan_table_an)
        DBSession.add(user_david_table_an)
        DBSession.add(user_daniel_table_an)

        batch = Batch.create()
        amendements_an[0].location.batch = batch
        amendements_an[1].location.batch = batch

        user_ronan_table_an.add_amendement(amendements_an[0])
        user_david_table_an.add_amendement(amendements_an[1])
        amendement = Amendement.create(
            lecture=lecture_an, article=article1_an, num=777, position=3
        )
        user_daniel_table_an.add_amendement(amendement)

    driver.get(f"{lecture_an_url}/amendements/")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    input_field = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) input"
    )
    input_field.send_keys(input_text)
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == filtered
    assert driver.current_url == f"{lecture_an_url}/amendements/?{kind}={input_text}"

    # Restore initial state.
    input_field.send_keys(Keys.BACKSPACE * len(input_text))
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    assert driver.current_url == f"{lecture_an_url}/amendements/"

    # Check filters are active on URL (re)load.
    driver.get(f"{lecture_an_url}/amendements/?{kind}={input_text}")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == filtered
    input_field = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) input"
    )
    input_field.send_keys(Keys.BACKSPACE * len(input_text))
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    assert driver.current_url == f"{lecture_an_url}/amendements/"


@pytest.mark.parametrize(
    "column_index,kind,initial,filtered",
    [
        ("3", "gouvernemental", ["666", "999", "777 Gouv."], ["777 Gouv."]),
        ("4", "emptytable", ["", "", "David"], ["", ""]),
        ("5", "emptyavis", ["", "", "#check"], ["", ""]),
    ],
)
def test_column_filtering_by_checkbox(
    wsgi_server,
    driver,
    lecture_an,
    lecture_an_url,
    article1_an,
    amendements_an,
    user_david_table_an,
    column_index,
    kind,
    initial,
    filtered,
):
    from zam_repondeur.models import Amendement, DBSession

    with transaction.manager:
        DBSession.add(user_david_table_an)
        amendement = Amendement.create(
            lecture=lecture_an,
            article=article1_an,
            num=777,
            position=3,
            auteur="LE GOUVERNEMENT",
        )
        amendement.user_content.avis = "Favorable"
        user_david_table_an.add_amendement(amendement)

    driver.get(f"{lecture_an_url}/amendements/")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    label = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) label[for='{kind}']"
    )
    label.click()
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == filtered
    assert driver.current_url == f"{lecture_an_url}/amendements/?{kind}=1"

    # Restore initial state.
    label.click()
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    assert driver.current_url == f"{lecture_an_url}/amendements/"

    # Check filters are active on URL (re)load.
    driver.get(f"{lecture_an_url}/amendements/?{kind}=1")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == filtered
    label = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) label[for='{kind}']"
    )
    label.click()
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    assert driver.current_url == f"{lecture_an_url}/amendements/"


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
        ("4", "222", "amendement", ["111", "333", "222"], ["222"]),
    ],
)
def test_column_filtering_by_value_for_missions(
    wsgi_server,
    driver,
    lecture_plf2018_an_premiere_lecture_seance_publique_2,
    article1_plf2018_an_premiere_lecture_seance_publique_2,
    amendements_plf2018_an_premiere_lecture_seance_publique_2,
    column_index,
    input_text,
    kind,
    initial,
    filtered,
):
    from zam_repondeur.models import Amendement, DBSession

    LECTURE_URL = (
        f"{wsgi_server.application_url}"
        f"dossiers/"
        f"{lecture_plf2018_an_premiere_lecture_seance_publique_2.dossier.url_key}/"
        f"lectures/{lecture_plf2018_an_premiere_lecture_seance_publique_2.url_key}"
    )
    with transaction.manager:
        amendement = Amendement.create(
            lecture=lecture_plf2018_an_premiere_lecture_seance_publique_2,
            article=article1_plf2018_an_premiere_lecture_seance_publique_2,
            num=222,
            position=3,
            mission_titre="Mission Action extérieure de l'État",
            mission_titre_court="Action ext.",
        )
        DBSession.add(amendement)

    driver.get(f"{LECTURE_URL}/amendements/")
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
        == f"{LECTURE_URL}/amendements/?{kind}={input_text.replace(' ', '+')}"
    )

    # Restore initial state.
    input_field.send_keys(Keys.BACKSPACE * len(input_text))
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    assert driver.current_url == f"{LECTURE_URL}/amendements/"

    # Check filters are active on URL (re)load.
    driver.get(f"{LECTURE_URL}/amendements/?{kind}={input_text}")
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == filtered
    input_field = driver.find_element_by_css_selector(
        f"thead tr.filters th:nth-child({column_index}) input"
    )
    input_field.send_keys(Keys.BACKSPACE * len(input_text))
    trs = driver.find_elements_by_css_selector(f"tbody tr:not(.hidden-{kind})")
    assert extract_column_text(column_index, trs) == initial
    assert driver.current_url == f"{LECTURE_URL}/amendements/"
