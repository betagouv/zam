import os

import pytest
import responses

from zam_aspirateur.amendements.fetch_an import build_url

HERE = os.path.dirname(__file__)
SAMPLE_DATA_DIR = os.path.join(os.path.dirname(HERE), "sample_data")


def read_sample_data(basename):
    filename = os.path.join(SAMPLE_DATA_DIR, basename)
    with open(filename, "rb") as file_:
        return file_.read()


@responses.activate
def test_fetch_and_parse_all():
    from zam_aspirateur.amendements.fetch_an import fetch_and_parse_all

    responses.add(
        responses.GET,
        build_url(14, "4072"),
        body=read_sample_data("an_liste.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(14, "4072", 177),
        body=read_sample_data("an_177.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(14, "4072", 270),
        body=read_sample_data("an_270.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(14, "4072", 723),
        body=read_sample_data("an_723.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(14, "4072", 135),
        body=read_sample_data("an_135.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(14, "4072", 192),
        body=read_sample_data("an_192.xml"),
        status=200,
    )

    title, items = fetch_and_parse_all(14, "4072")

    assert title == "PLFSS 2017"
    assert len(items) == 5
    assert items[0].num == "177"
    assert items[1].num == "270"
    assert items[2].num == "723"
    assert items[3].num == "135"
    assert items[4].num == "192"


@responses.activate
def test_fetch_amendements():
    from zam_aspirateur.amendements.fetch_an import fetch_amendements

    responses.add(
        responses.GET,
        build_url(14, "4072"),
        body=read_sample_data("an_liste.xml"),
        status=200,
    )

    title, items = fetch_amendements(14, "4072")

    assert title == "PLFSS 2017"
    assert len(items) == 5
    assert items[0] == {
        "@alineaLabel": "S",
        "@auteurGroupe": "Les Républicains",
        "@auteurLabel": "M. DOOR",
        "@auteurLabelFull": "M. DOOR Jean-Pierre",
        "@discussionCommune": "",
        "@discussionCommuneAmdtPositon": "",
        "@discussionCommuneSsAmdtPositon": "",
        "@discussionIdentique": "20386",
        "@discussionIdentiqueAmdtPositon": "debut",
        "@discussionIdentiqueSsAmdtPositon": "",
        "@missionLabel": "",
        "@numero": "177",
        "@parentNumero": "",
        "@place": "Article 3",
        "@position": "001/772",
        "@sort": "Rejeté",
    }


@responses.activate
def test_fetch_amendements_not_found():
    from zam_aspirateur.amendements.fetch_an import fetch_amendements, NotFound

    responses.add(responses.GET, build_url(14, "4072"), status=404)

    with pytest.raises(NotFound):
        fetch_amendements(14, "4072")


@responses.activate
def test_fetch_amendement():
    from zam_aspirateur.amendements.fetch_an import fetch_amendement
    from zam_aspirateur.amendements.models import Amendement

    responses.add(
        responses.GET,
        build_url(14, "4072", 177),
        body=read_sample_data("an_177.xml"),
        status=200,
    )

    amendement = fetch_amendement(14, "4072", 177)

    assert amendement == Amendement(
        subdiv_type="article",
        subdiv_num="3",
        subdiv_mult="",
        subdiv_pos="",
        alinea="",
        num="177",
        rectif=0,
        auteur="Door Jean-Pierre",
        matricule="267289",
        groupe="707869",
        date_depot=None,
        sort=None,
        discussion_commune=None,
        identique=None,
        dispositif='<p style="text-align: justify;">Supprimer cet article.</p>',
        objet=None,
        resume='<p style="text-align: justify;">Amendement d&#8217;appel.</p>\n<p style="text-align: justify;">Pour couvrir les d&#233;passements attendus de l&#8217;ONDAM pour 2016, cet article pr&#233;voit un pr&#233;l&#232;vement de 200 millions d&#8217;&#8364; sur les fonds de roulement de l&#8217;association nationale pour la formation permanente du personnel hospitalier (ANFH) et du fonds pour l&#8217;emploi hospitalier (FEH) pour financer le <span>fonds pour la modernisation des &#233;tablissements de sant&#233; publics et priv&#233;s</span>(FMESPP) en remplacement de cr&#233;dit de l&#8217;ONDAM. Il participe donc &#224; la pr&#233;sentation insinc&#232;re de la construction de l&#8217;ONDAM, d&#233;nonc&#233;e par le Comit&#233; d&#8217;alerte le 12 octobre dernier.</p>',  # noqa
        avis=None,
        observations=None,
        reponse=None,
    )


@responses.activate
def test_fetch_amendement_gouvernement():
    from zam_aspirateur.amendements.fetch_an import fetch_amendement

    responses.add(
        responses.GET,
        build_url(14, "4072", 723),
        body=read_sample_data("an_723.xml"),
        status=200,
    )

    amendement = fetch_amendement(14, "4072", 723)

    assert amendement.gouvernemental is True
    assert amendement.groupe == ""


@responses.activate
def test_fetch_amendement_commission():
    from zam_aspirateur.amendements.fetch_an import fetch_amendement

    responses.add(
        responses.GET,
        build_url(14, "4072", 135),
        body=read_sample_data("an_135.xml"),
        status=200,
    )

    amendement = fetch_amendement(14, "4072", 135)

    assert amendement.gouvernemental is False
    assert amendement.auteur == "Bapt Gérard"
    assert amendement.groupe == ""


@responses.activate
def test_fetch_amendement_apres():
    from zam_aspirateur.amendements.fetch_an import fetch_amendement

    responses.add(
        responses.GET,
        build_url(14, "4072", 192),
        body=read_sample_data("an_192.xml"),
        status=200,
    )

    amendement = fetch_amendement(14, "4072", 192)

    assert amendement.subdiv_type == "article"
    assert amendement.subdiv_num == "8"
    assert amendement.subdiv_mult == ""
    assert amendement.subdiv_pos == "apres"


@responses.activate
def test_fetch_amendement_not_found():
    from zam_aspirateur.amendements.fetch_an import fetch_amendement, NotFound

    responses.add(responses.GET, build_url(14, "4072", 177), status=404)

    with pytest.raises(NotFound):
        fetch_amendement(14, "4072", 177)
