import pytest
import transaction
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

pytestmark = pytest.mark.flaky(max_runs=5)


def test_visionneuse_detail_amendement(
    wsgi_server, driver, lecture_an_url, amendements_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendements_an[0].user_content.avis = "Favorable"
        amendements_an[0].auteur = "M. Content"
        amendements_an[0].groupe = "Les Heureux"
        DBSession.add_all(amendements_an)

    driver.get(f"{lecture_an_url}/articles/article.1../reponses#amdt-666")

    article = driver.find_element_by_css_selector("article")
    header = article.find_element_by_css_selector("header")
    assert header.find_element_by_css_selector("h2").text == "Amendement 666"
    assert (
        header.find_element_by_css_selector(".authors").text
        == "M. Content (Les Heureux)"
    )
    assert header.find_element_by_css_selector("p .avis").text == "Favorable"
    assert not article.find_element_by_css_selector(".reponse-detail").is_displayed()
    assert not article.find_element_by_css_selector(".amendement-detail").is_displayed()


def test_visionneuse_detail_amendement_reponse(
    wsgi_server, driver, lecture_an_url, amendements_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendements_an[0].user_content.avis = "Favorable"
        amendements_an[0].user_content.reponse = "La réponse"
        DBSession.add_all(amendements_an)

    driver.get(f"{lecture_an_url}/articles/article.1../reponses#amdt-666")

    article = driver.find_element_by_css_selector("article")
    header = article.find_element_by_css_selector("header")
    header.find_element_by_link_text("Réponse").click()
    assert article.find_element_by_css_selector(".reponse-detail").is_displayed()
    assert not article.find_element_by_css_selector(".amendement-detail").is_displayed()
    assert "La réponse" in article.find_element_by_css_selector(".reponse-detail").text
    article.find_element_by_css_selector(".reponse-detail").find_element_by_link_text(
        "Replier"
    ).click()
    assert not article.find_element_by_css_selector(".reponse-detail").is_displayed()


def test_visionneuse_detail_amendement_texte(
    wsgi_server, driver, lecture_an_url, amendements_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendements_an[0].user_content.avis = "Favorable"
        amendements_an[0].corps = "Le corps"
        DBSession.add_all(amendements_an)

    driver.get(f"{lecture_an_url}/articles/article.1../reponses#amdt-666")

    article = driver.find_element_by_css_selector("article")
    header = article.find_element_by_css_selector("header")

    # Unfold
    header.find_element_by_link_text("Texte").click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of(article.find_element_by_css_selector(".amendement-detail"))
    )
    assert "Le corps" in article.find_element_by_css_selector(".amendement-detail").text
    assert not article.find_element_by_css_selector(".reponse-detail").is_displayed()

    # Fold again
    button = article.find_element_by_css_selector(
        ".amendement-detail"
    ).find_element_by_link_text("Replier")
    assert button.is_displayed()
    button.click()
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element(
            article.find_element_by_css_selector(".amendement-detail")
        )
    )


def test_visionneuse_detail_amendement_reponse_then_texte(
    wsgi_server, driver, lecture_an_url, amendements_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        amendements_an[0].user_content.avis = "Favorable"
        amendements_an[0].user_content.reponse = "La réponse"
        amendements_an[0].user_content.objet = "L’objet"
        DBSession.add_all(amendements_an)

    driver.get(f"{lecture_an_url}/articles/article.1../reponses#amdt-666")

    article = driver.find_element_by_css_selector("article")
    header = article.find_element_by_css_selector("header")
    header.find_element_by_link_text("Réponse").click()
    assert article.find_element_by_css_selector(".reponse-detail").is_displayed()
    assert not article.find_element_by_css_selector(".amendement-detail").is_displayed()
    header.find_element_by_link_text("Texte").click()
    assert not article.find_element_by_css_selector(".reponse-detail").is_displayed()
    assert article.find_element_by_css_selector(".amendement-detail").is_displayed()
