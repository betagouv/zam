import json
from datetime import date
from operator import attrgetter
from pathlib import Path

import pytest
import responses
import transaction


HERE = Path(__file__)
SAMPLE_DATA_DIR = HERE.parent / "sample_data" / "senat"


def read_sample_data(basename):
    return (SAMPLE_DATA_DIR / basename).read_bytes()


@pytest.fixture
def dossier_plf(db):
    from zam_repondeur.models import Dossier

    with transaction.manager:
        dossier = Dossier.create(
            uid="DLR5L15N36733", titre="Budget : loi de finances 2019"
        )

    return dossier


@pytest.fixture
def texte_senat(db):
    # TODO: reuse existing texte or better, create fixtures for PLF2019.
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            uid="baz",
            type_=TypeTexte.PROJET,
            chambre=Chambre.SENAT,
            session=2017,
            numero=63,
            titre_long="long",
            titre_court="court",
            date_depot=date(2017, 10, 11),
        )

    return texte


@responses.activate
def test_aspire_senat(app, lecture_senat):
    from zam_repondeur.fetch.senat.amendements import Senat
    from zam_repondeur.models import DBSession
    from zam_repondeur.models.events.amendement import (
        AmendementRectifie,
        CorpsAmendementModifie,
        ExposeAmendementModifie,
    )

    sample_data = read_sample_data("jeu_complet_2017-2018_63.csv")

    responses.add(
        responses.GET,
        "https://www.senat.fr/amendements/2017-2018/63/jeu_complet_2017-2018_63.csv",
        body=sample_data,
        status=200,
    )

    odsen_data = read_sample_data("ODSEN_GENERAL.csv")

    responses.add(
        responses.GET,
        "https://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv",
        body=odsen_data,
        status=200,
    )

    json_data = json.loads(read_sample_data("liste_discussion_63.json"))

    responses.add(
        responses.GET,
        "https://www.senat.fr/enseance/2017-2018/63/liste_discussion.json",
        json=json_data,
        status=200,
    )

    DBSession.add(lecture_senat)

    source = Senat()

    amendements, created, errored = source.fetch(lecture_senat)

    # All amendements are fetched
    assert len(amendements) == 595

    # Check details of #1
    amendement = [amendement for amendement in amendements if amendement.num == 1][0]
    assert amendement.num == 1
    assert amendement.rectif == 1
    assert amendement.article.num == "7"
    assert amendement.article.pos == "après"
    assert amendement.parent is None

    events = sorted(amendement.events, key=attrgetter("created_at"), reverse=True)

    assert len(events) == 3
    assert isinstance(events[0], ExposeAmendementModifie)
    assert events[0].created_at is not None
    assert events[0].user is None
    assert events[0].data["old_value"] == ""
    assert events[0].data["new_value"].startswith("<p>Cet amendement vise")
    assert events[0].render_summary() == "L’exposé de l’amendement a été initialisé"

    assert isinstance(events[1], CorpsAmendementModifie)
    assert events[1].created_at is not None
    assert events[1].user is None
    assert events[1].data["old_value"] == ""
    assert events[1].data["new_value"].startswith("<p>Après l’article")
    assert events[1].render_summary() == "Le corps de l’amendement a été initialisé"

    assert isinstance(events[2], AmendementRectifie)
    assert events[2].created_at is not None
    assert events[2].user is None
    assert events[2].data["old_value"] == 0
    assert events[2].data["new_value"] == 1
    assert events[2].render_summary() == "L’amendement a été rectifié"

    # Check that #596 has a parent
    sous_amendement = [
        amendement for amendement in amendements if amendement.num == 596
    ][0]
    assert sous_amendement.parent.num == 229
    assert sous_amendement.parent.rectif == 1


@responses.activate
def test_aspire_senat_again_with_irrecevable(app, lecture_senat):
    from zam_repondeur.fetch.senat.amendements import Senat
    from zam_repondeur.models import DBSession
    from zam_repondeur.models.events.amendement import AmendementIrrecevable

    sample_data = read_sample_data("jeu_complet_2017-2018_63.csv")

    responses.add(
        responses.GET,
        "https://www.senat.fr/amendements/2017-2018/63/jeu_complet_2017-2018_63.csv",
        body=sample_data,
        status=200,
    )
    # On second call we want an irrecevable.
    responses.add(
        responses.GET,
        "https://www.senat.fr/amendements/2017-2018/63/jeu_complet_2017-2018_63.csv",
        body=sample_data.decode("latin-1")
        .replace(
            "Adopté\t//www.senat.fr/amendements/2017-2018/63/Amdt_1.html",
            "Irrecevable\t//www.senat.fr/amendements/2017-2018/63/Amdt_1.html",
        )
        .encode("latin-1"),
        status=200,
    )

    odsen_data = read_sample_data("ODSEN_GENERAL.csv")

    responses.add(
        responses.GET,
        "https://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv",
        body=odsen_data,
        status=200,
    )

    json_data = json.loads(read_sample_data("liste_discussion_63.json"))

    responses.add(
        responses.GET,
        "https://www.senat.fr/enseance/2017-2018/63/liste_discussion.json",
        json=json_data,
        status=200,
    )

    DBSession.add(lecture_senat)

    source = Senat()

    amendements, created, errored = source.fetch(lecture_senat)
    amendement = [amendement for amendement in amendements if amendement.num == 1][0]
    assert len(amendement.events) == 3

    amendements, created, errored = source.fetch(lecture_senat)
    amendement = [amendement for amendement in amendements if amendement.num == 1][0]
    assert len(amendement.events) == 4

    assert isinstance(amendement.events[3], AmendementIrrecevable)
    assert amendement.events[3].created_at is not None
    assert amendement.events[3].user is None
    assert amendement.events[3].data["old_value"] == "Adopté"
    assert amendement.events[3].data["new_value"] == "Irrecevable"
    assert (
        amendement.events[3].render_summary()
        == "L’amendement a été déclaré irrecevable par les services du Sénat"
    )


@responses.activate
def test_aspire_senat_again_with_irrecevable_transfers_to_index(
    app, lecture_senat, user_david_table_an
):
    from zam_repondeur.fetch.senat.amendements import Senat
    from zam_repondeur.models import DBSession
    from zam_repondeur.models.events.amendement import (
        AmendementIrrecevable,
        AmendementTransfere,
    )

    sample_data = read_sample_data("jeu_complet_2017-2018_63.csv")

    responses.add(
        responses.GET,
        "https://www.senat.fr/amendements/2017-2018/63/jeu_complet_2017-2018_63.csv",
        body=sample_data,
        status=200,
    )
    # On second call we want an irrecevable.
    responses.add(
        responses.GET,
        "https://www.senat.fr/amendements/2017-2018/63/jeu_complet_2017-2018_63.csv",
        body=sample_data.decode("latin-1")
        .replace(
            "Adopté\t//www.senat.fr/amendements/2017-2018/63/Amdt_1.html",
            "Irrecevable\t//www.senat.fr/amendements/2017-2018/63/Amdt_1.html",
        )
        .encode("latin-1"),
        status=200,
    )

    odsen_data = read_sample_data("ODSEN_GENERAL.csv")

    responses.add(
        responses.GET,
        "https://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv",
        body=odsen_data,
        status=200,
    )

    json_data = json.loads(read_sample_data("liste_discussion_63.json"))

    responses.add(
        responses.GET,
        "https://www.senat.fr/enseance/2017-2018/63/liste_discussion.json",
        json=json_data,
        status=200,
    )

    DBSession.add(lecture_senat)

    source = Senat()

    # Let's fetch a new amendement
    amendements, created, errored = source.fetch(lecture_senat)
    amendement = [amendement for amendement in amendements if amendement.num == 1][0]
    assert len(amendement.events) == 3

    # Put it on a user table
    DBSession.add(user_david_table_an)
    user_david_table_an.amendements.append(amendement)
    assert user_david_table_an.amendements == [amendement]
    assert amendement.user_table == user_david_table_an

    # Now fetch the same amendement again (now irrecevable)
    amendements, created, errored = source.fetch(lecture_senat)
    amendement = [amendement for amendement in amendements if amendement.num == 1][0]
    assert len(amendement.events) == 5  # two more

    # An irrecevable event has been created
    assert any(isinstance(event, AmendementIrrecevable) for event in amendement.events)

    # An automatic transfer event has been created
    assert any(isinstance(event, AmendementTransfere) for event in amendement.events)
    transfer_event = next(
        event for event in amendement.events if isinstance(event, AmendementTransfere)
    )
    assert transfer_event.user is None
    assert transfer_event.data["old_value"] == "David (david@example.com)"
    assert transfer_event.data["new_value"] == ""
    assert transfer_event.render_summary() == (
        "L’amendement a été remis automatiquement sur l’index"
    )

    # The amendement is now on the index
    assert amendement.user_table is None
    assert user_david_table_an.amendements == []


@responses.activate
def test_aspire_senat_plf2019_1re_partie(app, texte_senat, dossier_plf):
    from zam_repondeur.fetch.senat.amendements import Senat
    from zam_repondeur.models import DBSession, Lecture

    with transaction.manager:
        texte_senat.numero = 146
        lecture = Lecture.create(
            chambre="senat",
            session="2018-2019",
            texte=texte_senat,
            partie=1,
            titre="Numéro lecture – Titre lecture sénat",
            organe="PO78718",
            dossier=dossier_plf,
        )

    sample_data = read_sample_data("jeu_complet_2018-2019_146.csv")

    responses.add(
        responses.GET,
        "https://www.senat.fr/amendements/2018-2019/146/jeu_complet_2018-2019_146.csv",
        body=sample_data,
        status=200,
    )

    odsen_data = read_sample_data("ODSEN_GENERAL.csv")

    responses.add(
        responses.GET,
        "https://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv",
        body=odsen_data,
        status=200,
    )

    json_data = json.loads(read_sample_data("liste_discussion_103393.json"))

    responses.add(
        responses.GET,
        "https://www.senat.fr/enseance/2018-2019/146/liste_discussion_103393.json",
        json=json_data,
        status=200,
    )

    DBSession.add(lecture)

    source = Senat()

    amendements, created, errored = source.fetch(lecture)

    # All amendements from part 1 are fetched
    assert len(amendements) == 1005


@responses.activate
def test_aspire_senat_plf2019_2e_partie(app, texte_senat, dossier_plf):
    from zam_repondeur.fetch.senat.amendements import Senat
    from zam_repondeur.models import DBSession, Lecture

    with transaction.manager:
        texte_senat.numero = 146
        lecture = Lecture.create(
            chambre="senat",
            session="2018-2019",
            texte=texte_senat,
            partie=2,
            titre="Numéro lecture – Titre lecture sénat",
            organe="PO78718",
            dossier=dossier_plf,
        )

    sample_data = read_sample_data("jeu_complet_2018-2019_146.csv")

    responses.add(
        responses.GET,
        "https://www.senat.fr/amendements/2018-2019/146/jeu_complet_2018-2019_146.csv",
        body=sample_data,
        status=200,
    )

    odsen_data = read_sample_data("ODSEN_GENERAL.csv")

    responses.add(
        responses.GET,
        "https://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv",
        body=odsen_data,
        status=200,
    )

    json_data = json.loads(read_sample_data("liste_discussion_103394.json"))

    responses.add(
        responses.GET,
        "https://www.senat.fr/enseance/2018-2019/146/liste_discussion_103394.json",
        json=json_data,
        status=200,
    )

    json_data = json.loads(read_sample_data("liste_discussion_103395.json"))

    responses.add(
        responses.GET,
        "https://www.senat.fr/enseance/2018-2019/146/liste_discussion_103395.json",
        json=json_data,
        status=200,
    )

    for i in range(103396, 103445 + 1):
        responses.add(
            responses.GET,
            f"https://www.senat.fr/enseance/2018-2019/146/liste_discussion_{i}.json",
            status=404,
        )

    DBSession.add(lecture)

    source = Senat()

    amendements, created, errored = source.fetch(lecture)

    # All amendements from part 2 are fetched
    assert len(amendements) == 35

    # Positions are unique
    positions = [amdt.position for amdt in amendements if amdt.position is not None]
    assert len(set(positions)) == len(positions) == 12


@responses.activate
def test_fetch_all(lecture_senat):
    from zam_repondeur.fetch.senat.amendements import _fetch_all

    sample_data = read_sample_data("jeu_complet_2017-2018_63.csv")

    responses.add(
        responses.GET,
        "https://www.senat.fr/amendements/2017-2018/63/jeu_complet_2017-2018_63.csv",
        body=sample_data,
        status=200,
    )

    items = _fetch_all(lecture_senat)

    assert len(items) == 595

    assert items[0] == {
        "Alinéa": " ",
        "Au nom de ": "",
        "Auteur ": "M. FRASSA",
        "Date de dépôt ": "2017-11-13",
        "Dispositif ": '<body><p style="text-align: justify;">Apr&#232;s l&#8217;article&#160;7</p><p style="text-align: justify;">Ins&#233;rer un article&#160;additionnel ainsi r&#233;dig&#233;&#160;:</p><p style="text-align: justify;">I.&#160;&#8211;&#160;Le code de la s&#233;curit&#233; sociale est ainsi modifi&#233;&#160;:</p><p style="text-align: justify;">1&#176;&#160;L&#8217;article&#160;L.&#160;136&#8209;6 est ainsi modifi&#233;&#160;:</p><p style="text-align: justify;">a) Le I&#160;bis&#160;est abrog&#233;&#160;;</p><p style="text-align: justify;">b) &#192; la premi&#232;re phase du premier alin&#233;a du III, la premi&#232;re occurrence du mot&#160;: &#171;&#160;&#224;&#160;&#187; est remplac&#233;e par le mot&#160;: &#171;&#160;et&#160;&#187;&#160;;</p><p style="text-align: justify;">2&#176;&#160;L&#8217;article&#160;L.&#160;136&#8209;7 est ainsi modifi&#233;&#160;:</p><p style="text-align: justify;">a) Le I&#160;bis&#160;est abrog&#233;&#160;;</p><p style="text-align: justify;">b) Le second alin&#233;a du VI est supprim&#233;&#160;;</p><p style="text-align: justify;">3&#176;&#160;L&#8217;article&#160;L.&#160;245&#8209;14 est ainsi modifi&#233;&#160;:</p><p style="text-align: justify;">a) &#192; la premi&#232;re phrase, les r&#233;f&#233;rences&#160;: &#171;&#160;aux I et II de&#160;&#187; sont remplac&#233;es par le mot&#160;: &#171;&#160;&#224;&#160;&#187;&#160;;</p><p style="text-align: justify;">b) La deuxi&#232;me phrase est supprim&#233;e&#160;;</p><p style="text-align: justify;">4&#176;&#160;Au premier alin&#233;a de l&#8217;article&#160;L.&#160;245&#8209;15, la deuxi&#232;me occurrence du mot&#160;: &#171;&#160;&#224;&#160;&#187; est remplac&#233;e par le mot&#160;: &#171;&#160;et&#160;&#187;.</p><p style="text-align: justify;">II.&#160;&#8211;&#160;L&#8217;ordonnance n&#176;&#160;96&#8209;50 du 24&#160;janvier 1996 relative au remboursement de la dette sociale est ainsi modifi&#233;e&#160;:</p><p style="text-align: justify;">1&#176;&#160;La seconde phrase du premier alin&#233;a du I de l&#8217;article&#160;15 est supprim&#233;e&#160;;</p><p style="text-align: justify;">2&#176;&#160;&#192; la premi&#232;re phrase du I de l&#8217;article&#160;16, les r&#233;f&#233;rences&#160;: &#171;&#160;aux I et I&#160;bis&#160;&#187; sont remplac&#233;s par les mots&#160;: &#171;&#160;au I&#160;&#187;.</p><p style="text-align: justify;">III.&#160;&#8211;&#160;1&#176;&#160;Les 1&#176;&#160;et 3&#176;&#160;du I et le 1&#176; du II s&#8217;appliquent aux revenus per&#231;us &#224; compter du 1<sup>er</sup>&#160;janvier 2012&#160;;</p><p style="text-align: justify;">2&#176;&#160;Les 2&#176;&#160;et 4&#176;&#160;du I s&#8217;appliquent aux plus&#8209;values r&#233;alis&#233;es au titre des cessions intervenues &#224; compter de la date de publication de la pr&#233;sente loi&#160;;</p><p style="text-align: justify;">3&#176;&#160;Le 2&#176;&#160;du II s&#8217;applique aux plus&#8209;values r&#233;alis&#233;es au titre des cessions intervenues &#224; compter du 1<sup>er</sup>&#160;janvier 2012.</p><p style="text-align: justify;">IV.&#160;&#8211;&#160;La perte de recettes r&#233;sultant pour les organismes de s&#233;curit&#233; sociale des I &#224; III est compens&#233;e, &#224; due concurrence, par la cr&#233;ation d&#8217;une taxe additionnelle aux droits pr&#233;vus aux articles 575 et 575&#160;A du code g&#233;n&#233;ral des imp&#244;ts.</p></body>          ',  # noqa
        "Fiche Sénateur": "//www.senat.fr/senfic/frassa_christophe_andre08018u.html",  # noqa
        "Nature ": "Amt",
        "Numéro ": "1 rect.",
        "Objet ": '<body><p style="text-align: justify;">Cet amendement vise &#224; rectifier une anomalie, celle de l&#8217;assujettissement des Fran&#231;ais &#233;tablis hors de France au paiement de la contribution sociale g&#233;n&#233;ralis&#233;e et de la contribution pour le remboursement de la dette sociale.</p><p style="text-align: justify;">En effet, la loi de finances rectificatives pour 2012 a &#233;tendu les pr&#233;l&#232;vements sociaux aux revenus immobiliers (revenus fonciers et plus-values immobili&#232;res) de source fran&#231;aise per&#231;us par les personnes physiques fiscalement domicili&#233;es hors de France.</p><p style="text-align: justify;">Par cette mesure, les Fran&#231;ais non-r&#233;sidents contribuent au financement des r&#233;gimes obligatoires de la s&#233;curit&#233; sociale, dont ils ne b&#233;n&#233;ficient pourtant pas dans la majorit&#233; des cas, leur protection sociale relevant soit d&#8217;un r&#233;gime volontaire de la Caisse des Fran&#231;ais de l&#8217;&#233;tranger soit d&#8217;un syst&#232;me de protection sociale de leur pays de r&#233;sidence.</p><p style="text-align: justify;">Il en r&#233;sulte une double imposition pour les contribuables non-r&#233;sidents affili&#233;s &#224; un r&#233;gime de s&#233;curit&#233; sociale dans leur pays de r&#233;sidence et assujettis de fait aux pr&#233;l&#232;vements sociaux &#224; la fois en France et dans le pays o&#249; ils r&#233;sident.</p><p style="text-align: justify;">Cette situation est contraire au droit de l&#8217;Union europ&#233;enne et particuli&#232;rement au R&#232;glement (CEE) n&#176; 1408/71 du Conseil, du 14 juin 1971, relatif &#224; l&#8217;application des r&#233;gimes de s&#233;curit&#233; sociale aux travailleurs salari&#233;s, aux travailleurs non-salari&#233;s et aux membres de leur famille qui se d&#233;placent &#224; l&#8217;int&#233;rieur de la Communaut&#233;, qui subordonne le paiement des cotisations sociales au b&#233;n&#233;fice du r&#233;gime obligatoire de s&#233;curit&#233; sociale.</p></body>',  # noqa
        "Sort ": "Adopté",
        "Subdivision ": "art. add. après Article 7",
        "Url amendement ": "//www.senat.fr/amendements/2017-2018/63/Amdt_1.html",
    }


@responses.activate
def test_fetch_all_buggy_csv(lecture_senat):
    from zam_repondeur.fetch.senat.amendements import _fetch_all

    sample_data = read_sample_data("jeu_complet_2018-2019_106.csv")

    responses.add(
        responses.GET,
        "https://www.senat.fr/amendements/2017-2018/63/jeu_complet_2017-2018_63.csv",
        body=sample_data,
        status=200,
    )

    items = _fetch_all(lecture_senat)

    assert len(items) == 2

    assert items[0] == {
        "Alinéa": "Amendement de suppression",
        "Au nom de ": "",
        "Auteur ": "Mme ESTROSI SASSONE",
        "Date de dépôt ": "2018-11-12",
        "Dispositif ": "<body><p>Supprimer cet article.</p></body>",
        "Fiche Sénateur": "//www.senat.fr/senfic/estrosi_sassone_dominique14187a.html",
        "Nature ": "Amt",
        "Numéro ": "1 rect. bis",
        "Objet ": (
            '<body><p style="text-align: justify;">Ins&#233;r&#233; par '
            "l&#8217;Assembl&#233;e nationale, cet article vise la "
            "cr&#233;ation d&#8217;un forfait de r&#233;orientation et "
            "d&#8217;un forfait de consultation aux urgences. Toutefois, les "
            "cons&#233;quences de cet article peuvent &#234;tre "
            "extr&#234;mement graves pour la sant&#233; des Fran&#231;ais sous "
            "couvert de vouloir r&#233;duire le temps d&#8217;attente dans les "
            "services d&#8217;urgences hospitali&#232;res.</p><p "
            'style="text-align: justify;">En effet, en &#233;tablissant un '
            "nouveau mode de tarification aux urgences qui pourrait "
            "s&#8217;&#233;lever de 20 &#224; 60 euros par &#233;tablissement "
            "et par r&#233;orientation de patient vers un m&#233;decin de "
            "ville pour une consultation ult&#233;rieure ou bien au sein "
            "d&#8217;un autre service hospitalier, deux risques sont "
            'encourus.</p><p style="text-align: justify;">Le premier risque '
            "est d&#8217;envoyer un mauvais signal comptable, qu&#8217;il "
            "serait pr&#233;f&#233;rable de r&#233;orienter plut&#244;t que de "
            "soigner notamment &#224; l&#8217;heure o&#249; la fiabilisation "
            "des comptes des &#233;tablissements est un facteur "
            "d&#233;terminant pour la r&#233;alisation des classements "
            'g&#233;n&#233;raux.</p><p style="text-align: justify;">Le second '
            "risque est m&#233;dical car si pour certaines pathologies "
            "simples, le dispositif peut &#234;tre pertinent, comment prendre "
            "la d&#233;cision de r&#233;orienter certains patients et avoir la "
            "certitude que toute urgence vitale est &#233;cart&#233;e, "
            "d&#8217;autant que lors des passages aux urgences, les "
            "ant&#233;c&#233;dents et les informations de sant&#233; sont "
            'g&#233;n&#233;ralement parcellaires.</p><p style="text-align: '
            'justify;">Enfin, l&#8217;article est parcellaire puisque se pose '
            "la question de la responsabilit&#233; de la direction des "
            "&#233;tablissements de soins et des personnels soignants. Sur qui "
            "reposeront les cons&#233;quences d&#8217;une &#233;ventuelle "
            "erreur de diagnostic ou de posologie pour un traitement ou bien "
            "d&#8217;un retard de prise en charge d&#251; &#224; la "
            "r&#233;orientation chez un m&#233;decin de ville plusieurs jours "
            "apr&#232;s le passage aux urgences qui aura peut-&#234;tre fait "
            "perdre un temps pr&#233;cieux dans la r&#233;alisation du "
            "diagnostic&#160;?</p><p>En th&#233;orie, si le refus de "
            "r&#233;orientation par le patient est pr&#233;vu, la pratique ne "
            "laissera gu&#232;re le choix et sera source d&#8217;une prise en "
            "charge complexifi&#233;e.</p></body>"
        ),
        "Sort ": "",
        "Subdivision ": "Article 29\xa0quinquies",
        "Url amendement ": "//www.senat.fr/amendements/2018-2019/106/Amdt_1.html",
    }

    assert items[1] == {
        "Alinéa": "68",
        "Au nom de ": "commission des affaires sociales",
        "Auteur ": "M. VANLERENBERGHE",
        "Date de dépôt ": "2018-11-13",
        "Dispositif ": (
            "<body><p>Apr&#232;s l&#8217;alin&#233;a "
            "68</p><p>Ins&#233;rer un alin&#233;a ainsi "
            "r&#233;dig&#233;&#160;:</p><p><!-- [if lte IE 7]> <link "
            'href="/css_legifrance/squelette_IE6.css" rel="stylesheet" '
            'type="text/css" media="screen">  <link '
            'href="/css_legifrance/commun_IE6.css" rel="stylesheet" '
            'type="text/css" media="screen"> <![endif]-->&#8230;) Au '
            "dernier alin&#233;a du m&#234;me III, les mots&#160;: &#171; "
            "40 % du produit des contributions vis&#233;es aux 1&#176; et "
            "2&#176; &#187; sont remplac&#233;s par les mots&#160;: "
            "&#171; 24 % du produit des contributions mentionn&#233;es "
            "aux 1&#176; et 3&#176; &#187;&#160;;</p></body>"
        ),
        "Fiche Sénateur": "//www.senat.fr/senfic/vanlerenberghe_jean_marie01034p.html",
        "Nature ": "Amt",
        "Numéro ": "629",
        "Objet ": "<body><p>Amendement de coordination.</p></body>",
        "Sort ": "Recevable art. 40 C / LOLF",
        "Subdivision ": "Article 19",
        "Url amendement ": "//www.senat.fr/amendements/2018-2019/106/Amdt_629.html",
    }


@responses.activate
def test_fetch_all_commission(texte_senat, lecture_senat):
    from zam_repondeur.fetch.senat.amendements import _fetch_all
    from zam_repondeur.models import DBSession

    with transaction.manager:
        texte_senat.numero = 583
        lecture_senat.texte = texte_senat
        DBSession.add(lecture_senat)

    sample_data = read_sample_data("jeu_complet_commission_2017-2018_583.csv")

    responses.add(
        responses.GET,
        "https://www.senat.fr/amendements/2017-2018/583/jeu_complet_2017-2018_583.csv",
        status=404,
    )

    responses.add(
        responses.GET,
        "https://www.senat.fr/amendements/commissions/2017-2018/583/jeu_complet_commission_2017-2018_583.csv",  # noqa
        body=sample_data,
        status=200,
    )

    items = _fetch_all(lecture_senat)

    assert len(items) == 434

    assert items[0] == {
        "Nature ": "Amt",
        "Numéro ": "COM-1",
        "Subdivision ": "Article 40",
        "Alinéa": "36",
        "Auteur ": "M. FORISSIER, rapporteur",
        "Au nom de ": "",
        "Date de dépôt ": "2018-06-21",
        "Dispositif ": "<body><p>Alin&#233;a 36</p><p>Apr&#232;s le mot :</p><p>services</p><p>Ins&#233;rer les mots :</p><p>ou &#224; des partenariats</p><p></p></body>                                                                                                                                                                                                                ",  # noqa
        "Objet ": "<body><p>Cet amendement vise &#224; inclure parmi les d&#233;penses pouvant &#234;tre d&#233;duites de la contribution financi&#232;re annuelle, en plus des contrats de sous-traitance et de prestations, les <b>d&#233;penses aff&#233;rentes &#224; des partenariats</b> avec les entreprises adapt&#233;es, les Esat et les travailleurs handicap&#233;s ind&#233;pendants.</p><p>En effet, le nouveau mode de d&#233;duction des montants de ces contrats de la contribution annuelle risque de moins inciter les employeurs &#224; leur conclusion. D'o&#249; l'int&#233;r&#234;t d'&#233;largir cette d&#233;duction aux autres actions qu'ils sont susceptibles de mener aupr&#232;s des EA et des Esat notamment.</p></body>                                                                                                                                                                                                                                                                                                                                                                                                                                                         ",  # noqa
        "Sort ": "Adopté",
        "Url amendement ": "//www.senat.fr/amendements/commissions/2017-2018/583/Amdt_COM-1.html",  # noqa
        "Fiche Sénateur": "//www.senat.fr/senfic/forissier_michel14087w.html",
    }


@responses.activate
def test_fetch_all_not_found(lecture_senat):
    from zam_repondeur.fetch.senat.amendements import _fetch_all, NotFound

    responses.add(
        responses.GET,
        "https://www.senat.fr/amendements/2017-2018/63/jeu_complet_2017-2018_63.csv",
        status=404,
    )

    responses.add(
        responses.GET,
        "https://www.senat.fr/amendements/commissions/2017-2018/63/jeu_complet_commission_2017-2018_63.csv",  # noqa
        status=404,
    )

    with pytest.raises(NotFound):
        _fetch_all(lecture_senat)


@responses.activate
def test_fetch_discussion_details(texte_senat, lecture_senat):
    from zam_repondeur.fetch.senat.derouleur import _fetch_discussion_details
    from zam_repondeur.models import DBSession

    with transaction.manager:
        texte_senat.numero = 610
        lecture_senat.session = "2016-2017"
        lecture_senat.texte = texte_senat
        DBSession.add(lecture_senat)

    json_data = json.loads(read_sample_data("liste_discussion_610.json"))

    responses.add(
        responses.GET,
        "https://www.senat.fr/encommission/2016-2017/610/liste_discussion.json",
        json=json_data,
        status=200,
    )

    data = list(_fetch_discussion_details(lecture_senat, "commission"))

    assert len(data) == 1
    assert data[0] == json_data


@responses.activate
def test_fetch_discussion_details_empty_when_url_not_found(lecture_senat):
    from zam_repondeur.fetch.senat.derouleur import _fetch_discussion_details

    responses.add(
        responses.GET,
        "https://www.senat.fr/encommission/2017-2018/63/liste_discussion.json",
        status=404,
    )

    assert list(_fetch_discussion_details(lecture_senat, "commission")) == []


@responses.activate
def test_fetch_and_parse_discussion_details_empty_and_logs_when_url_not_found(
    lecture_senat, caplog
):
    from zam_repondeur.fetch.senat.derouleur import fetch_and_parse_discussion_details

    responses.add(
        responses.GET,
        "https://www.senat.fr/encommission/2017-2018/63/liste_discussion.json",
        status=404,
    )

    assert fetch_and_parse_discussion_details(lecture_senat, phase="commission") == []

    url = "https://www.senat.fr/encommission/2017-2018/63/liste_discussion.json"
    assert f"Could not fetch {url}" in [rec.message for rec in caplog.records]


@responses.activate
def test_fetch_and_parse_discussion_details_parent_before(lecture_senat, caplog):
    from zam_repondeur.fetch.senat.derouleur import fetch_and_parse_discussion_details

    data = json.loads(read_sample_data("liste_discussion_63-short-parent-before.json"))

    responses.add(
        responses.GET,
        "https://www.senat.fr/encommission/2017-2018/63/liste_discussion.json",
        json=data,
        status=200,
    )

    details = fetch_and_parse_discussion_details(lecture_senat, phase="commission")

    assert len(details) == 2
    assert details[0].parent_num == 31
    assert details[1].parent_num is None


@responses.activate
def test_fetch_and_parse_discussion_details_parent_missing(lecture_senat, caplog):
    from zam_repondeur.fetch.senat.derouleur import fetch_and_parse_discussion_details

    data = json.loads(read_sample_data("liste_discussion_63-short-parent-missing.json"))

    responses.add(
        responses.GET,
        "https://www.senat.fr/encommission/2017-2018/63/liste_discussion.json",
        json=data,
        status=200,
    )

    details = fetch_and_parse_discussion_details(lecture_senat, phase="commission")

    assert len(details) == 2
    assert details[0].parent_num is None
    assert details[1].parent_num is None
    assert f"Unknown parent amendement 1234" in [rec.message for rec in caplog.records]


def test_derouleur_urls(lecture_senat):
    from zam_repondeur.fetch.senat.derouleur import derouleur_urls

    assert list(derouleur_urls(lecture_senat, "seance")) == [
        "https://www.senat.fr/enseance/2017-2018/63/liste_discussion.json"
    ]


def test_derouleur_urls_plf2019_1re_partie(texte_senat, dossier_plf):
    from zam_repondeur.fetch.senat.derouleur import derouleur_urls
    from zam_repondeur.models import Lecture

    texte_senat.numero = 146
    lecture = Lecture.create(
        chambre="senat",
        session="2018-2019",
        texte=texte_senat,
        partie=1,
        titre="Première lecture – Séance publique (1re partie)",
        organe="PO78718",
        dossier=dossier_plf,
    )

    assert list(derouleur_urls(lecture, "seance")) == [
        "https://www.senat.fr/enseance/2018-2019/146/liste_discussion_103393.json"
    ]


def test_derouleur_urls_plf2019_2e_partie(texte_senat, dossier_plf):
    from zam_repondeur.fetch.senat.derouleur import derouleur_urls
    from zam_repondeur.models import Lecture

    texte_senat.numero = 146
    lecture = Lecture.create(
        chambre="senat",
        session="2018-2019",
        texte=texte_senat,
        partie=2,
        titre="Première lecture – Séance publique (2e partie)",
        organe="PO78718",
        dossier=dossier_plf,
    )

    urls = list(derouleur_urls(lecture, "seance"))
    assert len(urls) > 1
    assert (
        urls[0]
        == "https://www.senat.fr/enseance/2018-2019/146/liste_discussion_103427.json"
    )
    assert (
        urls[-1]
        == "https://www.senat.fr/enseance/2018-2019/146/liste_discussion_103394.json"
    )


@pytest.mark.parametrize("numero,partie", [("I-12", 1), ("II-4", 2), ("18", None)])
def test_parse_partie(numero, partie):
    from zam_repondeur.fetch.senat.amendements import parse_partie

    assert parse_partie(numero) == partie
