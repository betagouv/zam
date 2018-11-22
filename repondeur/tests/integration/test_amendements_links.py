import transaction

from .helpers import find_header_by_index


def test_repondeur_does_not_contains_link_to_visionneuse_if_no_avis(
    wsgi_server, browser, lecture_an, amendements_an
):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    browser.get(f"{LECTURE_URL}/amendements")
    secondary_nav = browser.find_element_by_css_selector(".nav.secondary")
    assert not secondary_nav.text.endswith("Voir le dossier de banc")


def test_repondeur_contains_link_to_visionneuse_if_avis(
    wsgi_server, browser, lecture_an, amendements_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendements_an[0].avis = "Favorable"
        DBSession.add_all(amendements_an)

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    browser.get(f"{LECTURE_URL}/amendements")
    secondary_nav = browser.find_element_by_css_selector(".nav.secondary")
    assert secondary_nav.text.endswith("Voir le dossier de banc")


def test_amendement_line_has_unitary_pdf_link(
    wsgi_server, browser, lecture_an, amendements_an
):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    browser.get(f"{LECTURE_URL}/amendements")
    download_td = browser.find_element_by_css_selector("td:nth-child(7)")
    download_link = download_td.find_element_by_css_selector("a")
    assert (
        download_link.get_attribute("href")
        == f"{LECTURE_URL}/amendements/666/download_amendement"
    )


def test_column_sorting_changes_edit_url_on_the_fly(
    wsgi_server, browser, lecture_an, amendements_an
):
    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    browser.get(f"{LECTURE_URL}/amendements")
    find_header_by_index(1, browser.find_element_by_css_selector("thead")).click()
    assert browser.current_url == f"{LECTURE_URL}/amendements?sort=1asc"
    avis_td = browser.find_element_by_css_selector("td:nth-child(5)")
    avis_link = avis_td.find_element_by_css_selector("a")
    assert avis_link.get_attribute("href") == f"{LECTURE_URL}/amendements/666/reponse"
    avis_link.click()
    assert browser.current_url == (
        f"{LECTURE_URL}/amendements/666/reponse?"
        f"back=%2Flectures%2F{lecture_an.url_key}%2Famendements%3Fsort%3D1asc"
    )
