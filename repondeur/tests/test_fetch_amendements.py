from collections import OrderedDict
import transaction
from unittest.mock import patch


def test_fetch_amendements_senat(app, lecture_senat, article1_senat, amendements_senat):
    from zam_repondeur.fetch import get_amendements
    from zam_repondeur.models import Amendement, DBSession
    from zam_repondeur.fetch.senat.senateurs.models import Senateur

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
        "zam_repondeur.fetch.senat.derouleur._fetch_discussion_details"
    ) as mock_fetch_discussion_details, patch(
        "zam_repondeur.fetch.senat.amendements.fetch_and_parse_senateurs"
    ) as mock_fetch_and_parse_senateurs:
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
        mock_fetch_discussion_details.return_value = {
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
        mock_fetch_and_parse_senateurs.return_value = {
            "01034P": Senateur(
                matricule="01034P",
                qualite="M.",
                nom="Vanlerenberghe",
                prenom="Jean-Marie",
                groupe="UC",
            )
        }

        amendements, created, errored = get_amendements(lecture_senat)

    assert [amendement.num for amendement in amendements] == [6666, 7777, 9999]
    assert created == 1
    assert errored == []

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
    from zam_repondeur.fetch import get_amendements
    from zam_repondeur.models import Amendement, DBSession

    amendement_999 = amendements_an[1]
    amendement_999.avis = "Favorable"
    amendement_999.observations = "Observations"
    amendement_999.reponse = "Réponse"
    DBSession.add(amendement_999)

    initial_modified_at_999 = amendement_999.modified_at

    with patch(
        "zam_repondeur.fetch.an.amendements.fetch_amendements"
    ) as mock_fetch_amendements, patch(
        "zam_repondeur.fetch.an.amendements._retrieve_amendement"
    ) as mock_retrieve_amendement:
        mock_fetch_amendements.return_value = [
            {"@numero": "666", "@discussionCommune": "", "@discussionIdentique": ""},
            {"@numero": "777", "@discussionCommune": "", "@discussionIdentique": ""},
            {"@numero": "999", "@discussionCommune": "", "@discussionIdentique": ""},
        ]

        def dynamic_return_value(lecture, numero):
            return {
                "division": {
                    "titre": "Article 1",
                    "type": "ARTICLE",
                    "avantApres": "",
                    "divisionRattache": "ARTICLE 1",
                },
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

        amendements, created, errored = get_amendements(lecture_an)

    assert [amendement.num for amendement in amendements] == [666, 777, 999]
    assert created == 1
    assert errored == []

    # Check that the response was preserved on the updated amendement
    amendement_999 = DBSession.query(Amendement).filter(Amendement.num == 999).one()
    assert amendement_999.avis == "Favorable"
    assert amendement_999.observations == "Observations"
    assert amendement_999.reponse == "Réponse"

    # Check that the position was changed on the updated amendement
    assert amendement_999.position == 3

    # Check that the modified date was updated
    assert amendement_999.modified_at > amendement_999.created_at
    assert amendement_999.modified_at > initial_modified_at_999

    # Check that the position was set for the new amendement
    amendement_777 = DBSession.query(Amendement).filter(Amendement.num == 777).one()
    assert amendement_777.position == 2

    # Check that the modified date was initialized
    assert amendement_777.modified_at is not None
    assert amendement_777.modified_at == amendement_777.created_at


def test_fetch_amendements_with_errored(app, lecture_an, article1_an, amendements_an):
    from zam_repondeur.fetch import get_amendements
    from zam_repondeur.models import Amendement, DBSession
    from zam_repondeur.fetch.exceptions import NotFound

    DBSession.add(lecture_an)

    with patch(
        "zam_repondeur.fetch.an.amendements.fetch_amendements"
    ) as mock_fetch_amendements, patch(
        "zam_repondeur.fetch.an.amendements._retrieve_amendement"
    ) as mock_retrieve_amendement:
        mock_fetch_amendements.return_value = [
            {"@numero": "666", "@discussionCommune": "", "@discussionIdentique": ""},
            {"@numero": "777", "@discussionCommune": "", "@discussionIdentique": ""},
            {"@numero": "999", "@discussionCommune": "", "@discussionIdentique": ""},
        ]
        mock_retrieve_amendement.side_effect = NotFound

        amendements, created, errored = get_amendements(lecture_an)

    assert amendements == []
    assert created == 0
    assert errored == ["666", "777", "999"]
    assert DBSession.query(Amendement).count() == len(amendements_an) == 2
