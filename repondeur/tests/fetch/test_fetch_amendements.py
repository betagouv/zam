from collections import OrderedDict
from textwrap import dedent
from unittest.mock import patch

import transaction

from fetch.mock_an import setup_mock_responses


def test_fetch_amendements_senat(app, lecture_senat, article1_senat, amendements_senat):
    from zam_repondeur.services.fetch import get_amendements
    from zam_repondeur.models import Amendement, DBSession
    from zam_repondeur.services.fetch.missions import MissionRef

    # Add a response to one of the amendements
    with transaction.manager:
        amendement = amendements_senat[1]
        amendement.user_content.avis = "Favorable"
        amendement.user_content.objet = "Objet"
        amendement.user_content.reponse = "Réponse"

        # The object is no longer bound to a session here, as it was created in a
        # previous transaction, so we add it to the current session to make sure that
        # our changes will be committed with the current transaction
        DBSession.add(amendement)

    # Update amendements
    with patch(
        "zam_repondeur.services.fetch.senat.amendements._fetch_all"
    ) as mock_fetch_all, patch(
        "zam_repondeur.services.fetch.senat.derouleur._fetch_discussion_details"
    ) as mock_fetch_discussion_details:
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
        mock_fetch_discussion_details.return_value = [
            (
                {
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
                            "signet": "../../textes/2017-2018/63.html#AMELI_SUB_4__Article_3",  # noqa
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
                },
                MissionRef(titre="", titre_court=""),
            )
        ]

        DBSession.add(lecture_senat)

        amendements, created, errored = get_amendements(lecture_senat)

    assert [amendement.num for amendement in amendements] == [6666, 7777, 9999]
    assert created == 1
    assert errored == []

    # Check that the response was preserved on the updated amendement
    amendement = DBSession.query(Amendement).filter(Amendement.num == 9999).one()
    assert amendement.user_content.avis == "Favorable"
    assert amendement.user_content.objet == "Objet"
    assert amendement.user_content.reponse == "Réponse"

    # Check that the position was changed on the updated amendement
    assert amendement.position == 3

    # Check that the position is set for the new amendement
    amendement = DBSession.query(Amendement).filter(Amendement.num == 7777).one()
    assert amendement.position == 2


def test_fetch_amendements_an(app, lecture_an, article1_an):
    from zam_repondeur.services.fetch import get_amendements
    from zam_repondeur.models import Amendement, DBSession

    Amendement.create(lecture=lecture_an, article=article1_an, num=6, position=1)

    amendement_9 = Amendement.create(
        lecture=lecture_an,
        article=article1_an,
        num=9,
        position=2,
        avis="Favorable",
        objet="Objet",
        reponse="Réponse",
    )

    with patch(
        "zam_repondeur.services.fetch.an.amendements.fetch_discussion_list"
    ) as mock_fetch_discussion_list, patch(
        "zam_repondeur.services.fetch.an.amendements._retrieve_amendement"
    ) as mock_retrieve_amendement:
        mock_fetch_discussion_list.return_value = [
            {"@numero": "6", "@discussionCommune": "", "@discussionIdentique": ""},
            {"@numero": "7", "@discussionCommune": "", "@discussionIdentique": ""},
            {"@numero": "9", "@discussionCommune": "", "@discussionIdentique": ""},
        ]

        def dynamic_return_value(lecture, numero_prefixe):
            from zam_repondeur.services.fetch.exceptions import NotFound

            if numero_prefixe not in {"6", "7", "9"}:
                raise NotFound

            return {
                "division": {
                    "titre": "Article 1",
                    "type": "ARTICLE",
                    "avantApres": "",
                    "divisionRattache": "ARTICLE 1",
                },
                "numero": numero_prefixe,
                "numeroLong": numero_prefixe,
                "auteur": {
                    "tribunId": "642788",
                    "groupeTribunId": "730964",
                    "estGouvernement": "0",
                    "estRapporteur": "0",
                    "nom": "Véran",
                    "prenom": "Olivier",
                },
                "exposeSommaire": "<p>Amendement r&#233;dactionnel.</p>",
                "dispositif": "<p>&#192; l&#8217;alin&#233;a&#160;8, substituer</p>",
                "numeroParent": OrderedDict({"@xsi:nil": "true"}),
                "sortEnSeance": OrderedDict({"@xsi:nil": "true"}),
                "etat": "AC",
                "retireAvantPublication": "0",
            }

        mock_retrieve_amendement.side_effect = dynamic_return_value

        amendements, created, errored = get_amendements(lecture_an)

    assert [amendement.num for amendement in amendements] == [6, 7, 9]
    assert created == 1
    assert errored == []

    amendement_9 = DBSession.query(Amendement).filter(Amendement.num == 9).one()
    # Check that the response was preserved on the updated amendement
    assert amendement_9.user_content.avis == "Favorable"
    assert amendement_9.user_content.objet == "Objet"
    assert amendement_9.user_content.reponse == "Réponse"

    # Check that the auteur key leads to matricule, groupe and auteur filling
    assert amendement_9.matricule == "642788"
    assert amendement_9.groupe == "La République en Marche"
    assert amendement_9.auteur == "Véran Olivier"

    # Check that the position was changed on the updated amendement
    assert amendement_9.position == 3

    # Check that the position was set for the new amendement
    amendement_7 = DBSession.query(Amendement).filter(Amendement.num == 7).one()
    assert amendement_7.position == 2


def test_fetch_amendements_an_with_mission(app, lecture_an, article1_an):
    from zam_repondeur.services.fetch import get_amendements
    from zam_repondeur.models import Amendement, DBSession

    Amendement.create(lecture=lecture_an, article=article1_an, num=6, position=1)

    amendement_9 = Amendement.create(
        lecture=lecture_an,
        article=article1_an,
        num=9,
        position=2,
        avis="Favorable",
        objet="Objet",
        reponse="Réponse",
    )

    with patch(
        "zam_repondeur.services.fetch.an.amendements.fetch_discussion_list"
    ) as mock_fetch_discussion_list, patch(
        "zam_repondeur.services.fetch.an.amendements._retrieve_amendement"
    ) as mock_retrieve_amendement:
        mock_fetch_discussion_list.return_value = [
            {"@numero": "6", "@discussionCommune": "", "@discussionIdentique": ""},
            {"@numero": "7", "@discussionCommune": "", "@discussionIdentique": ""},
            {"@numero": "9", "@discussionCommune": "", "@discussionIdentique": ""},
        ]

        def dynamic_return_value(lecture, numero_prefixe):
            from zam_repondeur.services.fetch.exceptions import NotFound

            if numero_prefixe not in {"6", "7", "9"}:
                raise NotFound

            return {
                "division": {
                    "titre": "Article 1",
                    "type": "ARTICLE",
                    "avantApres": "",
                    "divisionRattache": "ARTICLE 1",
                },
                "numero": numero_prefixe,
                "numeroLong": numero_prefixe,
                "auteur": {
                    "tribunId": "642788",
                    "groupeTribunId": "730964",
                    "estGouvernement": "0",
                    "estRapporteur": "0",
                    "nom": "Véran",
                    "prenom": "Olivier",
                },
                "exposeSommaire": "<p>Amendement r&#233;dactionnel.</p>",
                "dispositif": "<p>&#192; l&#8217;alin&#233;a&#160;8, substituer</p>",
                "numeroParent": OrderedDict({"@xsi:nil": "true"}),
                "sortEnSeance": OrderedDict({"@xsi:nil": "true"}),
                "etat": "AC",
                "retireAvantPublication": "0",
                "missionVisee": "Mission « Outre-mer »",
            }

        mock_retrieve_amendement.side_effect = dynamic_return_value

        amendements, created, errored = get_amendements(lecture_an)

    assert [amendement.num for amendement in amendements] == [6, 7, 9]
    assert created == 1
    assert errored == []

    amendement_9 = DBSession.query(Amendement).filter(Amendement.num == 9).one()
    # Check that the mission is created
    assert amendement_9.mission.titre == "Mission « Outre-mer »"
    assert amendement_9.mission.titre_court == "Outre-mer"


def test_fetch_amendements_an_without_auteur_key(app, lecture_an, article1_an, caplog):
    from zam_repondeur.services.fetch import get_amendements
    from zam_repondeur.models import Amendement, DBSession

    amendement_6 = Amendement.create(
        lecture=lecture_an, article=article1_an, num=6, position=1
    )
    DBSession.add(amendement_6)

    amendement_9 = Amendement.create(
        lecture=lecture_an,
        article=article1_an,
        num=9,
        position=2,
        avis="Favorable",
        objet="Objet",
        reponse="Réponse",
    )
    DBSession.add(amendement_9)

    with patch(
        "zam_repondeur.services.fetch.an.amendements.fetch_discussion_list"
    ) as mock_fetch_discussion_list, patch(
        "zam_repondeur.services.fetch.an.amendements._retrieve_amendement"
    ) as mock_retrieve_amendement:
        mock_fetch_discussion_list.return_value = [
            {"@numero": "6", "@discussionCommune": "", "@discussionIdentique": ""},
            {"@numero": "7", "@discussionCommune": "", "@discussionIdentique": ""},
            {"@numero": "9", "@discussionCommune": "", "@discussionIdentique": ""},
        ]

        def dynamic_return_value(lecture, numero_prefixe):
            from zam_repondeur.services.fetch.exceptions import NotFound

            if numero_prefixe not in {"6", "7", "9"}:
                raise NotFound

            return {
                "division": {
                    "titre": "Article 1",
                    "type": "ARTICLE",
                    "avantApres": "",
                    "divisionRattache": "ARTICLE 1",
                },
                "numero": numero_prefixe,
                "numeroLong": numero_prefixe,
                # No auteur key.
                "exposeSommaire": "<p>Amendement r&#233;dactionnel.</p>",
                "dispositif": "<p>&#192; l&#8217;alin&#233;a&#160;8, substituer</p>",
                "numeroParent": OrderedDict({"@xsi:nil": "true"}),
                "sortEnSeance": OrderedDict({"@xsi:nil": "true"}),
                "etat": "AC",
                "retireAvantPublication": "0",
            }

        mock_retrieve_amendement.side_effect = dynamic_return_value

        amendements, created, errored = get_amendements(lecture_an)

    assert [amendement.num for amendement in amendements] == [6, 7, 9]
    assert created == 1
    assert errored == []

    for num in [6, 7, 9]:
        assert any(
            record.levelname == "WARNING"
            and record.message.startswith(f"Unknown auteur for amendement {num}")
            for record in caplog.records
        )

    amendement_9 = DBSession.query(Amendement).filter(Amendement.num == 9).one()
    # Check that the missing auteur key leads to an explicit string
    assert amendement_9.matricule == ""
    assert amendement_9.groupe == "Non trouvé"
    assert amendement_9.auteur == "Non trouvé"


def test_fetch_amendements_an_without_group_tribun_id(
    app, lecture_an, article1_an, caplog
):
    from zam_repondeur.services.fetch import get_amendements
    from zam_repondeur.models import Amendement, DBSession

    amendement_6 = Amendement.create(
        lecture=lecture_an, article=article1_an, num=6, position=1
    )
    DBSession.add(amendement_6)

    amendement_9 = Amendement.create(
        lecture=lecture_an,
        article=article1_an,
        num=9,
        position=2,
        avis="Favorable",
        objet="Objet",
        reponse="Réponse",
    )
    DBSession.add(amendement_9)

    with patch(
        "zam_repondeur.services.fetch.an.amendements.fetch_discussion_list"
    ) as mock_fetch_discussion_list, patch(
        "zam_repondeur.services.fetch.an.amendements._retrieve_amendement"
    ) as mock_retrieve_amendement:
        mock_fetch_discussion_list.return_value = [
            {"@numero": "6", "@discussionCommune": "", "@discussionIdentique": ""},
            {"@numero": "7", "@discussionCommune": "", "@discussionIdentique": ""},
            {"@numero": "9", "@discussionCommune": "", "@discussionIdentique": ""},
        ]

        def dynamic_return_value(lecture, numero_prefixe):
            from zam_repondeur.services.fetch.exceptions import NotFound

            if numero_prefixe not in {"6", "7", "9"}:
                raise NotFound

            return {
                "division": {
                    "titre": "Article 1",
                    "type": "ARTICLE",
                    "avantApres": "",
                    "divisionRattache": "ARTICLE 1",
                },
                "numero": numero_prefixe,
                "numeroLong": numero_prefixe,
                "auteur": {
                    "tribunId": "642788",
                    # Sort of empty groupeTribunId
                    "groupeTribunId": OrderedDict({"@xsi:nil": "true"}),
                    "estGouvernement": "0",
                    "estRapporteur": "0",
                    "nom": "Véran",
                    "prenom": "Olivier",
                },
                "exposeSommaire": "<p>Amendement r&#233;dactionnel.</p>",
                "dispositif": "<p>&#192; l&#8217;alin&#233;a&#160;8, substituer</p>",
                "numeroParent": OrderedDict({"@xsi:nil": "true"}),
                "sortEnSeance": OrderedDict({"@xsi:nil": "true"}),
                "etat": "AC",
                "retireAvantPublication": "0",
            }

        mock_retrieve_amendement.side_effect = dynamic_return_value

        amendements, created, errored = get_amendements(lecture_an)

    assert [amendement.num for amendement in amendements] == [6, 7, 9]
    assert created == 1
    assert errored == []

    for num in [6, 7, 9]:
        assert any(
            record.levelname == "WARNING"
            and record.message.startswith(
                f"Missing groupeTribunId value for amendement {num}"
            )
            for record in caplog.records
        )

    amendement_9 = DBSession.query(Amendement).filter(Amendement.num == 9).one()
    # Check that the empty group key leads to an explicit string
    assert amendement_9.matricule == "642788"
    assert amendement_9.groupe == "Non précisé"
    assert amendement_9.auteur == "Véran Olivier"


def test_fetch_amendements_an_with_unknown_group_tribun_id(
    app, lecture_an, article1_an, caplog
):
    from zam_repondeur.services.fetch import get_amendements
    from zam_repondeur.models import Amendement, DBSession

    amendement_6 = Amendement.create(
        lecture=lecture_an, article=article1_an, num=6, position=1
    )
    DBSession.add(amendement_6)

    amendement_9 = Amendement.create(
        lecture=lecture_an,
        article=article1_an,
        num=9,
        position=2,
        avis="Favorable",
        objet="Objet",
        reponse="Réponse",
    )
    DBSession.add(amendement_9)

    with patch(
        "zam_repondeur.services.fetch.an.amendements.fetch_discussion_list"
    ) as mock_fetch_discussion_list, patch(
        "zam_repondeur.services.fetch.an.amendements._retrieve_amendement"
    ) as mock_retrieve_amendement:
        mock_fetch_discussion_list.return_value = [
            {"@numero": "6", "@discussionCommune": "", "@discussionIdentique": ""},
            {"@numero": "7", "@discussionCommune": "", "@discussionIdentique": ""},
            {"@numero": "9", "@discussionCommune": "", "@discussionIdentique": ""},
        ]

        def dynamic_return_value(lecture, numero_prefixe):
            from zam_repondeur.services.fetch.exceptions import NotFound

            if numero_prefixe not in {"6", "7", "9"}:
                raise NotFound

            return {
                "division": {
                    "titre": "Article 1",
                    "type": "ARTICLE",
                    "avantApres": "",
                    "divisionRattache": "ARTICLE 1",
                },
                "numero": numero_prefixe,
                "numeroLong": numero_prefixe,
                "auteur": {
                    "tribunId": "642788",
                    # Unknown groupeTribunId
                    "groupeTribunId": "Unknown",
                    "estGouvernement": "0",
                    "estRapporteur": "0",
                    "nom": "Véran",
                    "prenom": "Olivier",
                },
                "exposeSommaire": "<p>Amendement r&#233;dactionnel.</p>",
                "dispositif": "<p>&#192; l&#8217;alin&#233;a&#160;8, substituer</p>",
                "numeroParent": OrderedDict({"@xsi:nil": "true"}),
                "sortEnSeance": OrderedDict({"@xsi:nil": "true"}),
                "etat": "AC",
                "retireAvantPublication": "0",
            }

        mock_retrieve_amendement.side_effect = dynamic_return_value

        amendements, created, errored = get_amendements(lecture_an)

    assert [amendement.num for amendement in amendements] == [6, 7, 9]
    assert created == 1
    assert errored == []

    for num in [6, 7, 9]:
        assert any(
            record.levelname == "WARNING"
            and record.message.startswith(
                f"Unknown groupe tribun 'POUnknown' in groupes for amendement {num}"
            )
            for record in caplog.records
        )

    amendement_9 = DBSession.query(Amendement).filter(Amendement.num == 9).one()
    # Check that the wrong group key leads to an explicit string
    assert amendement_9.matricule == "642788"
    assert amendement_9.groupe == "Non trouvé"
    assert amendement_9.auteur == "Véran Olivier"


def test_fetch_amendements_with_errored(app, lecture_an, article1_an, amendements_an):
    from zam_repondeur.services.fetch import get_amendements
    from zam_repondeur.models import Amendement, DBSession
    from zam_repondeur.services.fetch.exceptions import NotFound

    DBSession.add(lecture_an)

    with patch(
        "zam_repondeur.services.fetch.an.amendements.fetch_discussion_list"
    ) as mock_fetch_discussion_list, patch(
        "zam_repondeur.services.fetch.an.amendements._retrieve_amendement"
    ) as mock_retrieve_amendement:
        mock_fetch_discussion_list.return_value = [
            {"@numero": "6", "@discussionCommune": "", "@discussionIdentique": ""},
            {"@numero": "7", "@discussionCommune": "", "@discussionIdentique": ""},
            {"@numero": "9", "@discussionCommune": "", "@discussionIdentique": ""},
        ]
        mock_retrieve_amendement.side_effect = NotFound

        amendements, created, errored = get_amendements(lecture_an)

    assert amendements == []
    assert created == 0
    assert errored == ["6", "7", "9"]
    assert DBSession.query(Amendement).count() == len(amendements_an) == 2


def test_fetch_amendements_with_emptiness(app, lecture_an, article1_an, amendements_an):
    from zam_repondeur.services.fetch import get_amendements
    from zam_repondeur.models import Amendement, DBSession

    DBSession.add(lecture_an)

    with setup_mock_responses(
        lecture=lecture_an,
        liste=dedent(
            """\
            <?xml version="1.0" encoding="UTF-8"?>
            <amdtsParOrdreDeDiscussion></amdtsParOrdreDeDiscussion>
            """
        ),
        amendements=(),
    ):
        amendements, created, errored = get_amendements(lecture_an)

    assert amendements == []
    assert created == 0
    assert errored == []
    assert DBSession.query(Amendement).count() == len(amendements_an) == 2


def test_fetch_amendements_with_connection_errors(
    app, lecture_an, article1_an, amendements_an
):
    from requests.exceptions import ConnectionError
    from zam_repondeur.services.fetch import get_amendements
    from zam_repondeur.models import Amendement, DBSession

    DBSession.add(lecture_an)

    with patch(
        "zam_repondeur.services.fetch.an.amendements.fetch_discussion_list"
    ) as mock_fetch_discussion_list, patch(
        "zam_repondeur.services.fetch.an.amendements.cached_session.get"
    ) as mock_cached_session_get:
        mock_fetch_discussion_list.return_value = [
            {"@numero": "6", "@discussionCommune": "", "@discussionIdentique": ""},
            {"@numero": "7", "@discussionCommune": "", "@discussionIdentique": ""},
            {"@numero": "9", "@discussionCommune": "", "@discussionIdentique": ""},
        ]
        mock_cached_session_get.side_effect = ConnectionError

        amendements, created, errored = get_amendements(lecture_an)

    assert amendements == []
    assert created == 0
    assert errored == ["6", "7", "9"]
    assert DBSession.query(Amendement).count() == len(amendements_an) == 2


def test_fetch_update_amendements_an_with_batch_preserve_batch(
    app, lecture_an, article1_an, amendements_an_batch
):
    from zam_repondeur.services.fetch import get_amendements
    from zam_repondeur.models import Amendement, DBSession

    assert amendements_an_batch[0].batch.nums == [666, 999]

    with transaction.manager, patch(
        "zam_repondeur.services.fetch.an.amendements.fetch_discussion_list"
    ) as mock_fetch_discussion_list, patch(
        "zam_repondeur.services.fetch.an.amendements._retrieve_amendement"
    ) as mock_retrieve_amendement:
        DBSession.add(lecture_an)
        mock_fetch_discussion_list.return_value = [
            {"@numero": "666", "@discussionCommune": "", "@discussionIdentique": ""},
            {"@numero": "999", "@discussionCommune": "", "@discussionIdentique": ""},
        ]

        def dynamic_return_value(lecture, numero_prefixe):
            from zam_repondeur.services.fetch.exceptions import NotFound

            if numero_prefixe not in {"666", "999"}:
                raise NotFound

            return {
                "division": {
                    "titre": "Article 1",
                    "type": "ARTICLE",
                    "avantApres": "",
                    "divisionRattache": "ARTICLE 1",
                },
                "numero": numero_prefixe,
                "numeroLong": numero_prefixe,
                "auteur": {
                    "tribunId": "642788",
                    "groupeTribunId": "730964",
                    "estGouvernement": "0",
                    "estRapporteur": "0",
                    "nom": "Véran",
                    "prenom": "Olivier",
                },
                "exposeSommaire": "<p>Amendement r&#233;dactionnel.</p>",
                "dispositif": "<p>&#192; l&#8217;alin&#233;a&#160;8, substituer</p>",
                "numeroParent": OrderedDict({"@xsi:nil": "true"}),
                "sortEnSeance": OrderedDict({"@xsi:nil": "true"}),
                "etat": "AC",
                "retireAvantPublication": "0",
            }

        mock_retrieve_amendement.side_effect = dynamic_return_value

        amendements, created, errored = get_amendements(lecture_an)

    assert [amendement.num for amendement in amendements] == [666, 999]
    assert created == 0
    assert errored == []

    amendement_666 = DBSession.query(Amendement).filter(Amendement.num == 666).one()
    assert amendement_666.batch.nums == [666, 999]


def test_fetch_update_amendements_an_with_batch_and_changing_article(
    app, lecture_an, article1_an, amendements_an_batch
):
    from zam_repondeur.services.fetch import get_amendements
    from zam_repondeur.models import Amendement, DBSession
    from zam_repondeur.models.events.amendement import BatchUnset

    assert amendements_an_batch[0].batch.nums == [666, 999]

    with transaction.manager, patch(
        "zam_repondeur.services.fetch.an.amendements.fetch_discussion_list"
    ) as mock_fetch_discussion_list, patch(
        "zam_repondeur.services.fetch.an.amendements._retrieve_amendement"
    ) as mock_retrieve_amendement:
        DBSession.add(lecture_an)
        mock_fetch_discussion_list.return_value = [
            {"@numero": "666", "@discussionCommune": "", "@discussionIdentique": ""},
            {"@numero": "999", "@discussionCommune": "", "@discussionIdentique": ""},
        ]

        def dynamic_return_value(lecture, numero_prefixe):
            from zam_repondeur.services.fetch.exceptions import NotFound

            if numero_prefixe not in {"666", "999"}:
                raise NotFound

            return {
                "division": {
                    "titre": "Article 1",
                    "type": "ARTICLE",
                    "avantApres": "avant",
                    "divisionRattache": "ARTICLE 1",
                },
                "numero": numero_prefixe,
                "numeroLong": numero_prefixe,
                "auteur": {
                    "tribunId": "642788",
                    "groupeTribunId": "730964",
                    "estGouvernement": "0",
                    "estRapporteur": "0",
                    "nom": "Véran",
                    "prenom": "Olivier",
                },
                "exposeSommaire": "<p>Amendement r&#233;dactionnel.</p>",
                "dispositif": "<p>&#192; l&#8217;alin&#233;a&#160;8, substituer</p>",
                "numeroParent": OrderedDict({"@xsi:nil": "true"}),
                "sortEnSeance": OrderedDict({"@xsi:nil": "true"}),
                "etat": "AC",
                "retireAvantPublication": "0",
            }

        mock_retrieve_amendement.side_effect = dynamic_return_value

        amendements, created, errored = get_amendements(lecture_an)

    assert [amendement.num for amendement in amendements] == [666, 999]
    assert created == 0
    assert errored == []

    for num in [666, 999]:
        amendement = DBSession.query(Amendement).filter(Amendement.num == num).one()
        assert amendement.batch is None

        event = next(e for e in amendement.events if isinstance(e, BatchUnset))
        assert event.render_summary() == (
            "Cet amendement a été sorti du lot dans lequel il était."
        )
