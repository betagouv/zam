from contextlib import contextmanager
from functools import partial

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from webtest.http import StopableWSGIServer

from .helpers import login, logout


@pytest.fixture(params=["firefox", "chrome"])
def driver(request, wsgi_server):
    factory = driver_factory(request.param)
    with factory() as _driver:

        # Add helper methods to the driver
        _driver.login = partial(login, _driver, wsgi_server.application_url)
        _driver.logout = partial(logout, _driver, wsgi_server.application_url)

        try:
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
    from zam_repondeur.visam.app import make_app

    settings = {**settings, "zam.auth_cookie_secure": False}
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
def seance_ccfp_url(wsgi_server, seance_ccfp):
    return f"{wsgi_server.application_url}seances/{seance_ccfp.slug}/"


@pytest.fixture
def lecture_seance_ccfp_url(seance_ccfp_url, lecture_seance_ccfp):
    return f"{seance_ccfp_url}textes/{lecture_seance_ccfp.dossier.slug}"
