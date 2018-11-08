import json
import transaction
from pathlib import Path
from unittest.mock import patch

import pytest
import responses


HERE = Path(__file__)
SAMPLE_DATA_DIR = HERE.parent / "sample_data"


def read_sample_data(basename):
    return (SAMPLE_DATA_DIR / basename).read_bytes()


@responses.activate
def test_aspire_senat(app, lecture_senat):
    from zam_repondeur.fetch.senat.amendements import aspire_senat

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

    amendements, created = aspire_senat(lecture_senat)

    # All amendements are fetched
    assert len(amendements) == 595

    # Check details of #1
    amendement = [amendement for amendement in amendements if amendement.num == 1][0]
    assert amendement.num == 1
    assert amendement.rectif == 1
    assert amendement.article.num == "7"
    assert amendement.article.pos == "après"
    assert amendement.parent is None

    # Check that #596 has a parent
    sous_amendement = [
        amendement for amendement in amendements if amendement.num == 596
    ][0]
    assert sous_amendement.parent.num == 229
    assert sous_amendement.parent.rectif == 1


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
def test_fetch_all_commission(lecture_senat):
    from zam_repondeur.models import DBSession
    from zam_repondeur.fetch.senat.amendements import _fetch_all

    with transaction.manager:
        lecture_senat.num_texte = 583
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
def test_fetch_discussion_details(lecture_senat):
    from zam_repondeur.fetch.senat.derouleur import _fetch_discussion_details
    from zam_repondeur.models import DBSession

    with transaction.manager:
        lecture_senat.session = "2016-2017"
        lecture_senat.num_texte = 610
        DBSession.add(lecture_senat)

    json_data = json.loads(read_sample_data("liste_discussion_610.json"))

    responses.add(
        responses.GET,
        "https://www.senat.fr/encommission/2016-2017/610/liste_discussion.json",
        json=json_data,
        status=200,
    )

    data = _fetch_discussion_details(lecture_senat, "commission")

    assert data == json_data


@responses.activate
def test_fetch_discussion_details_not_found(lecture_senat):
    from zam_repondeur.fetch.senat.derouleur import _fetch_discussion_details, NotFound

    responses.add(
        responses.GET,
        "https://www.senat.fr/encommission/2017-2018/63/liste_discussion.json",
        status=404,
    )

    with pytest.raises(NotFound):
        _fetch_discussion_details(lecture_senat, "commission")


def testfetch_and_parse_discussion_details_not_found(lecture_senat):
    from zam_repondeur.fetch.senat.derouleur import (
        fetch_and_parse_discussion_details,
        NotFound,
    )

    with patch(
        "zam_repondeur.fetch.senat.derouleur._fetch_discussion_details"
    ) as m_fetch:
        m_fetch.side_effect = NotFound

        amendements = fetch_and_parse_discussion_details(
            lecture_senat, phase="commission"
        )

    assert amendements == []
