from selenium.webdriver.support.ui import WebDriverWait

from zam_repondeur.auth import generate_auth_token
from zam_repondeur.services.users import repository


def login(driver, base_url, email):
    wait = WebDriverWait(driver, 1)

    # Click on authentication link
    token = generate_auth_token()
    repository.set_auth_token(email, token)
    driver.get(f"{base_url}authentification?token={token}")

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
