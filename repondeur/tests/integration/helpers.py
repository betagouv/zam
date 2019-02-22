from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException


def find_header_by_index(index, headers):
    return headers.find_element_by_css_selector(f"th:nth-child({index})")


def extract_column_text(index, trs):
    texts = []
    for tr in trs:
        td = tr.find_element_by_css_selector(f"td:nth-child({index})")
        text = td.text
        if not text:
            # Fallback on SVG reference name.
            try:
                text = td.find_element_by_tag_name("use").get_attribute("xlink:href")
            except NoSuchElementException:
                pass
        texts.append(text)
    return texts


def extract_item_text(selector, trs):
    return [item.find_element_by_css_selector(selector).text for item in trs]


def login(driver, base_url, email):
    wait = WebDriverWait(driver, 1)

    # Enter email on identification page
    identification_url = f"{base_url}identification"
    driver.get(identification_url)
    if driver.current_url.startswith(f"{base_url}lectures/"):
        return  # already logged in
    assert driver.find_element_by_css_selector("h1").text == "Entrer dans Zam"
    driver.find_element_by_css_selector("input[type='email']").send_keys(email)
    driver.find_element_by_css_selector("input[type='submit']").click()
    wait.until(lambda driver: not driver.current_url.startswith(identification_url))

    # Submit name on first login
    welcome_url = f"{base_url}bienvenue"
    if not driver.current_url.startswith(welcome_url):
        return  # name already known
    assert (
        driver.find_element_by_css_selector("h1").text
        == "C’est votre première connexion…"
    )
    driver.find_element_by_css_selector("input[type='submit']").click()
    wait.until(lambda driver: not driver.current_url.startswith(welcome_url))


def logout(driver, base_url, email):
    logout_url = f"{base_url}deconnexion"
    driver.get(logout_url)
    wait = WebDriverWait(driver, 1)
    wait.until(lambda driver: not driver.current_url.startswith(logout_url))
