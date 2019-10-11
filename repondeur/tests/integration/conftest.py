from contextlib import contextmanager

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from webtest.http import StopableWSGIServer

from .helpers import login


@pytest.fixture(params=["firefox", "chrome"])
def driver(request, wsgi_server, user_david):
    factory = driver_factory(request.param)
    with factory() as _driver:
        try:
            login(_driver, wsgi_server.application_url, user_david.email)
            yield _driver
        finally:
            _driver.quit()


def driver_factory(name):
    if name == "firefox":
        return firefox_driver
    elif name == "chrome":
        return chrome_driver


@contextmanager
def firefox_driver():
    try:
        yield HeadlessFirefox()
    except WebDriverException as e:
        if str(e).startswith("Message: 'geckodriver' executable needs to be in PATH."):
            pytest.skip("You need geckodriver to run browser tests in Firefox")
        else:
            raise


@contextmanager
def chrome_driver():
    try:
        yield HeadlessChrome()
    except WebDriverException as e:
        if str(e).startswith("Message: 'chromedriver' executable needs to be in PATH."):
            pytest.skip("You need chromedriver to run browser tests in Chrome")
        else:
            raise


@pytest.fixture
def wsgi_server(
    settings, db, mock_dossiers, mock_organes_acteurs, amendements_repository
):
    from zam_repondeur import make_app

    settings = {
        **settings,
        "zam.auth_cookie_secure": False,
        "zam.auth_cookie_http_only": False,
    }
    wsgi_app = make_app(None, **settings)
    server = StopableWSGIServer.create(wsgi_app)
    server.settings = settings
    yield server
    server.shutdown()


class HeadlessFirefox(webdriver.Firefox):
    def __init__(self):
        super().__init__(options=self.options())

    @staticmethod
    def options():
        firefox_options = webdriver.firefox.options.Options()
        firefox_options.add_argument("-headless")
        firefox_options.set_preference("dom.disable_beforeunload", False)
        return firefox_options

    def get(self, url):
        """
        Loads a web page in the current browser session.

        We override the default `get` to force a page refresh if the target URL is
        the currently open one, as Selenium / geckodriver / Firefox (not sure who is
        guilty here) will just skip the request in that case, even if the page has
        HTTP headers asking for it not to be cached.
        """
        if url == self.current_url:
            self.refresh()
        else:
            super().get(url)


class HeadlessChrome(webdriver.Chrome):
    def __init__(self):
        super().__init__(options=self.options())

    @staticmethod
    def options():
        chrome_options = webdriver.chrome.options.Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        return chrome_options


@pytest.fixture
def dossier_an_url(wsgi_server, lecture_an):
    return f"{wsgi_server.application_url}dossiers/{lecture_an.dossier.url_key}"


@pytest.fixture
def lecture_an_url(wsgi_server, lecture_an, dossier_an_url):
    return f"{dossier_an_url}/lectures/{lecture_an.url_key}"
