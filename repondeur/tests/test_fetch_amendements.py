from collections import OrderedDict
import transaction
from unittest.mock import patch


def test_fetch_amendements_senat(app, lecture_senat, article1_senat, amendements_senat):
    from zam_repondeur.models import Amendement, DBSession

    # Add a response to one of the amendements
    with transaction.manager:
        amendement = amendements_senat[1]
        amendement.avis = "Favorable"
        amendement.observations = "Observations"
        amendement.reponse = "Réponse"

        # The object is no longer bound to a session here, as it was created in a
        # previous transaction, so we add it to the current session to make sure that
        # our changes will be committed with the current transaction
        DBSession.add(amendement)

    # Update amendements
    with patch(
        "zam_repondeur.fetch.senat.amendements._fetch_all"
    ) as mock_fetch_all, patch(
        "zam_repondeur.fetch.senat.amendements._fetch_discussed"
    ) as mock_fetch_discussed:
        mock_fetch_all.return_value = (
            {
                "Numéro ": "6666",
                "Subdivision ": "Article 1",
                "Alinéa": "1",
                "Auteur ": "LE GOUVERNEMENT",
                "Date de dépôt ": "2017-11-13",
                "Fiche Sénateur": "",
                "Sort ": "Adopté",
                "Dispositif ": "",
                "Objet ": "",
            },
            {
                "Numéro ": "7777",
                "Subdivision ": "Article 1",
                "Alinéa": "1",
                "Auteur ": "LE GOUVERNEMENT",
                "Date de dépôt ": "2017-11-13",
                "Fiche Sénateur": "",
                "Sort ": "Adopté",
                "Dispositif ": "",
                "Objet ": "",
            },
            {
                "Numéro ": "9999",
                "Subdivision ": "Article 1",
                "Alinéa": "1",
                "Auteur ": "LE GOUVERNEMENT",
                "Date de dépôt ": "2017-11-13",
                "Fiche Sénateur": "",
                "Sort ": "Adopté",
                "Dispositif ": "",
                "Objet ": "",
            },
        )
        mock_fetch_discussed.return_value = {
            "info_generales": {
                "natureLoi": "Projet de loi",
                "intituleLoi": "Financement de la sécurité sociale pour 2018",
                "lecture": "1ère lecture",
                "tsgenhtml": "1531427548000",
                "idtxt": "103021",
                "nbAmdtsDeposes": "595",
                "nbAmdtsAExaminer": "0",
                "doslegsignet": "plfss2018",
            },
            "Subdivisions": [
                {
                    "libelle_subdivision": "Article 1",
                    "id_subdivision": "151610",
                    "signet": "../../textes/2017-2018/63.html#AMELI_SUB_4__Article_3",
                    "Amendements": [
                        {
                            "idAmendement": "1103376",
                            "posder": "1",
                            "subpos": "0",
                            "isSousAmendement": "false",
                            "idAmendementPere": "0",
                            "urlAmdt": "Amdt_31.html",
                            "typeAmdt": "Amt",
                            "num": "6666",
                            "libelleAlinea": "Al. 8",
                            "urlAuteur": "vanlerenberghe_jean_marie01034p.html",
                            "auteur": "M. VANLERENBERGHE",
                            "isDiscussionCommune": "false",
                            "isDiscussionCommuneIsolee": "false",
                            "isIdentique": "false",
                            "sort": "Adopté",
                            "isAdopte": "true",
                            "isRejete": "false",
                        },
                        {
                            "idAmendement": "1103376",
                            "posder": "1",
                            "subpos": "0",
                            "isSousAmendement": "false",
                            "idAmendementPere": "0",
                            "urlAmdt": "Amdt_31.html",
                            "typeAmdt": "Amt",
                            "num": "7777",
                            "libelleAlinea": "Al. 8",
                            "urlAuteur": "vanlerenberghe_jean_marie01034p.html",
                            "auteur": "M. VANLERENBERGHE",
                            "isDiscussionCommune": "false",
                            "isDiscussionCommuneIsolee": "false",
                            "isIdentique": "false",
                            "sort": "Adopté",
                            "isAdopte": "true",
                            "isRejete": "false",
                        },
                        {
                            "idAmendement": "1103376",
                            "posder": "1",
                            "subpos": "0",
                            "isSousAmendement": "false",
                            "idAmendementPere": "0",
                            "urlAmdt": "Amdt_31.html",
                            "typeAmdt": "Amt",
                            "num": "9999",
                            "libelleAlinea": "Al. 8",
                            "urlAuteur": "vanlerenberghe_jean_marie01034p.html",
                            "auteur": "M. VANLERENBERGHE",
                            "isDiscussionCommune": "false",
                            "isDiscussionCommuneIsolee": "false",
                            "isIdentique": "false",
                            "sort": "Adopté",
                            "isAdopte": "true",
                            "isRejete": "false",
                        },
                    ],
                }
            ],
        }

        resp = app.post("/lectures/senat.2017-2018.63.PO78718/fetch_amendements")

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/"

    resp = resp.follow()
    assert resp.status_code == 200
    assert "1 nouvel amendement récupéré." in resp.text

    # Check that the response was preserved on the updated amendement
    amendement = DBSession.query(Amendement).filter(Amendement.num == 9999).one()
    assert amendement.avis == "Favorable"
    assert amendement.observations == "Observations"
    assert amendement.reponse == "Réponse"

    # Check that the position was changed on the updated amendement
    assert amendement.position == 3

    # Check that the position is set for the new amendement
    amendement = DBSession.query(Amendement).filter(Amendement.num == 7777).one()
    assert amendement.position == 2


def test_fetch_amendements_an(app, lecture_an, article1_an, amendements_an):
    from zam_repondeur.models import Amendement, DBSession

    # Add a response to one of the amendements
    with transaction.manager:
        amendement = amendements_an[1]
        amendement.avis = "Favorable"
        amendement.observations = "Observations"
        amendement.reponse = "Réponse"

        # The object is no longer bound to a session here, as it was created in a
        # previous transaction, so we add it to the current session to make sure that
        # our changes will be committed with the current transaction
        DBSession.add(amendement)

    with patch(
        "zam_repondeur.fetch.an.amendements.fetch_amendements"
    ) as mock_fetch_amendements, patch(
        "zam_repondeur.fetch.an.amendements._retrieve_amendement"
    ) as mock_retrieve_amendement:
        mock_fetch_amendements.return_value = [
            {"@numero": "666"},
            {"@numero": "777"},
            {"@numero": "999"},
        ]

        def dynamic_return_value(lecture, numero, groups_folder):
            return {
                "division": {"titre": "Article 1", "type": "ARTICLE", "avantApres": ""},
                "numero": numero,
                "auteur": {
                    "tribunId": "642788",
                    "groupeTribunId": "730964",
                    "estGouvernement": "0",
                    "nom": "Véran",
                    "prenom": "Olivier",
                },
                "exposeSommaire": "<p>Amendement r&#233;dactionnel.</p>",
                "dispositif": "<p>&#192; l&#8217;alin&#233;a&#160;8, substituer</p>",
                "numeroParent": OrderedDict({"@xsi:nil": "true"}),
                "sortEnSeance": OrderedDict({"@xsi:nil": "true"}),
            }

        mock_retrieve_amendement.side_effect = dynamic_return_value

        resp = app.post("/lectures/an.15.269.PO717460/fetch_amendements")

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/"

    resp = resp.follow()
    assert resp.status_code == 200
    assert "1 nouvel amendement récupéré." in resp.text

    # Check that the response was preserved on the updated amendement
    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement.avis == "Favorable"
    assert amendement.observations == "Observations"
    assert amendement.reponse == "Réponse"

    # Check that the position was changed on the updated amendement
    assert amendement.position == 3

    # Check that the position is set for the new amendement
    amendement = DBSession.query(Amendement).filter(Amendement.num == 777).one()
    assert amendement.position == 2


def test_fetch_amendements_with_errored(app, lecture_an, article1_an, amendements_an):
    from zam_repondeur.models import Amendement

    with patch("zam_repondeur.views.lectures.get_amendements") as mock_get_amendements:
        mock_get_amendements.return_value = (
            [Amendement(lecture=lecture_an, article=article1_an, num=777, position=1)],
            1,
            ["111", "222"],
        )

        resp = app.post("/lectures/an.15.269.PO717460/fetch_amendements")

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/"

    resp = resp.follow()
    assert resp.status_code == 200
    assert "Les amendements 111, 222 n’ont pu être récupérés." in resp.text
    assert "1 nouvel amendement récupéré." in resp.text


def test_fetch_amendements_none(app, lecture_an):

    with patch("zam_repondeur.views.lectures.get_amendements") as mock_get_amendements:
        mock_get_amendements.return_value = [], 0, []

        resp = app.post("/lectures/an.15.269.PO717460/fetch_amendements")

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/"

    resp = resp.follow()
    assert resp.status_code == 200
    assert "Aucun amendement n’a pu être trouvé." in resp.text
