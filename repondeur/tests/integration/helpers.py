from selenium.webdriver.support.ui import WebDriverWait


def find_header_by_index(index, headers):
    return headers.find_element_by_css_selector(f"th:nth-child({index})")


def extract_column_text(index, trs):
    return [
        tr.find_element_by_css_selector(f"td:nth-child({index})").text for tr in trs
    ]


def login(driver, base_url, email):
    login_url = f"{base_url}identification"
    driver.get(login_url)
    driver.find_element_by_css_selector("input[type='email']").send_keys(email)
    driver.find_element_by_css_selector("input[type='submit']").click()
    wait = WebDriverWait(driver, 1)
    wait.until(lambda driver: not driver.current_url.startswith(login_url))


def logout(driver, base_url, email):
    logout_url = f"{base_url}deconnexion"
    driver.get(logout_url)
    wait = WebDriverWait(driver, 1)
    wait.until(lambda driver: not driver.current_url.startswith(logout_url))
