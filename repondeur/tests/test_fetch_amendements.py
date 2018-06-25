from unittest.mock import patch

import transaction


def html_text(text):
    return text.replace("'", "&#39;")


def test_fetch_amendements(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import Amendement, DBSession

    # Add a response to one of the amendements
    with transaction.manager:
        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
        amendement.avis = "Favorable"
        amendement.observations = "Observations"
        amendement.reponse = "Réponse"

    # Update amendements
    with patch("zam_repondeur.views.lectures.get_amendements") as mock_get_amendements:
        mock_get_amendements.return_value = [
            Amendement(
                chambre="an",
                session="15",
                num_texte=269,
                subdiv_type="article",
                subdiv_num="1",
                num=666,
                position=1,
            ),
            Amendement(
                chambre="an",
                session="15",
                num_texte=269,
                subdiv_type="article",
                subdiv_num="1",
                num=777,
                position=2,
            ),
            Amendement(
                chambre="an",
                session="15",
                num_texte=269,
                subdiv_type="article",
                subdiv_num="1",
                num=999,
                position=3,
            ),
        ]

        resp = app.post("/lectures/an/15/269/amendements/fetch")

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an/15/269/"

    resp = resp.follow()
    assert resp.status_code == 200
    assert html_text("1 nouvel amendement récupéré.") in resp.text
    assert html_text("1 amendement mis à jour.") in resp.text
    assert html_text("1 amendement inchangé.") in resp.text

    # Check that the response was preserved on the updated amendement
    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.avis == "Favorable"
    assert amendement.observations == "Observations"
    assert amendement.reponse == "Réponse"

    # Check that the position was changed on the updated amendement
    assert amendement.position == 3


def test_fetch_amendements_none(app, dummy_lecture):

    with patch("zam_repondeur.views.lectures.get_amendements") as mock_get_amendements:
        mock_get_amendements.return_value = []

        resp = app.post("/lectures/an/15/269/amendements/fetch")

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an/15/269/"

    resp = resp.follow()
    assert resp.status_code == 200
    assert html_text("Aucun amendement n'a pu être trouvé.") in resp.text
