import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from webtest.http import StopableWSGIServer


@pytest.fixture(scope="session")
def driver():
    options = webdriver.firefox.options.Options()
    options.add_argument("-headless")

    try:
        driver = webdriver.Firefox(options=options)
        yield driver
        driver.quit()
    except WebDriverException:
        pytest.skip("You need Firefox and geckodriver to run browser tests")


@pytest.fixture
def new_driver():
    options = webdriver.firefox.options.Options()
    options.add_argument("-headless")

    try:
        new_driver = webdriver.Firefox(options=options)
        yield new_driver
        new_driver.quit()
    except WebDriverException:
        pytest.skip("You need Firefox and geckodriver to run browser tests")


@pytest.fixture(scope="session")
def wsgi_server(wsgi_app):
    server = StopableWSGIServer.create(wsgi_app, port="8080")
    yield server
    server.shutdown()
