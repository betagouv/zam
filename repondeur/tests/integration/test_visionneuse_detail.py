import transaction


def test_visionneuse_detail_amendement(
    wsgi_server, browser, lecture_an, amendements_an
):
    from zam_repondeur.models import DBSession

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    with transaction.manager:
        amendements_an[0].avis = "Favorable"
        amendements_an[0].auteur = "M. Content"
        amendements_an[0].groupe = "Les Heureux"
        DBSession.add_all(amendements_an)

    browser.get(f"{LECTURE_URL}/articles/article.1../reponses#amdt-666")
    article = browser.find_element_by_css_selector("article")
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
    wsgi_server, browser, lecture_an, amendements_an
):
    from zam_repondeur.models import DBSession

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    with transaction.manager:
        amendements_an[0].avis = "Favorable"
        amendements_an[0].reponse = "La réponse"
        DBSession.add_all(amendements_an)

    browser.get(f"{LECTURE_URL}/articles/article.1../reponses#amdt-666")
    article = browser.find_element_by_css_selector("article")
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
    wsgi_server, browser, lecture_an, amendements_an
):
    from zam_repondeur.models import DBSession

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    with transaction.manager:
        amendements_an[0].avis = "Favorable"
        amendements_an[0].objet = "L’objet"
        DBSession.add_all(amendements_an)

    browser.get(f"{LECTURE_URL}/articles/article.1../reponses#amdt-666")
    article = browser.find_element_by_css_selector("article")
    header = article.find_element_by_css_selector("header")
    header.find_element_by_link_text("Texte").click()
    assert not article.find_element_by_css_selector(".reponse-detail").is_displayed()
    assert article.find_element_by_css_selector(".amendement-detail").is_displayed()
    assert "L’objet" in article.find_element_by_css_selector(".amendement-detail").text
    article.find_element_by_css_selector(
        ".amendement-detail"
    ).find_element_by_link_text("Replier").click()
    assert not article.find_element_by_css_selector(".amendement-detail").is_displayed()


def test_visionneuse_detail_amendement_reponse_then_texte(
    wsgi_server, browser, lecture_an, amendements_an
):
    from zam_repondeur.models import DBSession

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    with transaction.manager:
        amendements_an[0].avis = "Favorable"
        amendements_an[0].reponse = "La réponse"
        amendements_an[0].objet = "L’objet"
        DBSession.add_all(amendements_an)

    browser.get(f"{LECTURE_URL}/articles/article.1../reponses#amdt-666")
    article = browser.find_element_by_css_selector("article")
    header = article.find_element_by_css_selector("header")
    header.find_element_by_link_text("Réponse").click()
    assert article.find_element_by_css_selector(".reponse-detail").is_displayed()
    assert not article.find_element_by_css_selector(".amendement-detail").is_displayed()
    header.find_element_by_link_text("Texte").click()
    assert not article.find_element_by_css_selector(".reponse-detail").is_displayed()
    assert article.find_element_by_css_selector(".amendement-detail").is_displayed()
