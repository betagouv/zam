from textwrap import dedent

import pyperclip
import pytest
from selenium.webdriver.common.keys import Keys


@pytest.mark.parametrize(
    "initial,expected",
    [
        # Iso
        (
            dedent(
                """\
                foo.bar@sgg.pm.gouv.fr
                baz.qux@pm.gouv.fr"""
            ),
            dedent(
                """\
                foo.bar@sgg.pm.gouv.fr
                baz.qux@pm.gouv.fr"""
            ),
        ),
        # Outlook
        (
            "FOO Bar <foo.bar@sgg.pm.gouv.fr>; BAZ Qux <baz.qux@pm.gouv.fr>",
            dedent(
                """\
                foo.bar@sgg.pm.gouv.fr
                baz.qux@pm.gouv.fr"""
            ),
        ),
        # Mixed (one email has no associated name)
        (
            (
                "FOO Bar <foo.bar@sgg.pm.gouv.fr>; baz.qux@pm.gouv.fr; "
                "QUUX Quuz <quux.quuz@pm.gouv.fr>"
            ),
            dedent(
                """\
                foo.bar@sgg.pm.gouv.fr
                baz.qux@pm.gouv.fr
                quux.quuz@pm.gouv.fr"""
            ),
        ),
        # Classic comma
        (
            "foo.bar@sgg.pm.gouv.fr, baz.qux@pm.gouv.fr",
            dedent(
                """\
                foo.bar@sgg.pm.gouv.fr
                baz.qux@pm.gouv.fr"""
            ),
        ),
    ],
)
def test_dossier_paste_emails(wsgi_server, driver, dossier_an_url, initial, expected):
    if driver.options().headless:
        pytest.skip("Copy-pasting only available if browser not in headless mode.")
    driver.get(f"{dossier_an_url}/invite")
    emails_textarea = driver.find_element_by_css_selector('[name="emails"]')
    assert emails_textarea.is_displayed()
    pyperclip.copy(initial)
    emails_textarea.send_keys(Keys.CONTROL, "v")
    emails_textarea.send_keys(Keys.COMMAND, "v")  # MacOS.
    assert emails_textarea.get_attribute("value") == expected
