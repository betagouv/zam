import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from webtest.http import StopableWSGIServer


@pytest.fixture(scope="session")
def driver():
    try:
        driver = HeadlessFirefox()
        yield driver
        driver.quit()
    except WebDriverException:
        pytest.skip("You need Firefox and geckodriver to run browser tests")


@pytest.fixture(scope="session")
def wsgi_server(wsgi_app):
    server = StopableWSGIServer.create(wsgi_app, port="8080")
    yield server
    server.shutdown()


class HeadlessFirefox(webdriver.Firefox):
    def __init__(self):
        super().__init__(options=self.options())

    @staticmethod
    def options():
        firefox_options = webdriver.firefox.options.Options()
        firefox_options.add_argument("-headless")
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
