from pathlib import Path

import pytest
import responses

from zam_repondeur.fetch.an.amendements import build_url

HERE = Path(__file__)
SAMPLE_DATA_DIR = HERE.parent / "sample_data"


def read_sample_data(basename):
    return (SAMPLE_DATA_DIR / basename).read_text()


@responses.activate
def test_fetch_and_parse_all():
    from zam_repondeur.fetch.an.amendements import fetch_and_parse_all

    responses.add(
        responses.GET,
        build_url(14, 4072),
        body=read_sample_data("an_liste.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(14, 4072, 177),
        body=read_sample_data("an_177.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(14, 4072, 270),
        body=read_sample_data("an_270.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(14, 4072, 723),
        body=read_sample_data("an_723.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(14, 4072, 135),
        body=read_sample_data("an_135.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(14, 4072, 192),
        body=read_sample_data("an_192.xml"),
        status=200,
    )

    title, amendements, errored = fetch_and_parse_all(
        legislature=14, texte=4072, organe="PO717460", groups_folder=SAMPLE_DATA_DIR
    )

    assert title == "PLFSS 2017"
    assert len(amendements) == 5
    assert amendements[0].num == 177
    assert amendements[1].num == 270
    assert amendements[2].num == 723
    assert amendements[3].num == 135
    assert amendements[4].num == 192

    assert [amdt.position for amdt in amendements] == list(range(1, 6))
    assert errored == []


@responses.activate
def test_fetch_and_parse_all_with_404():
    from zam_repondeur.fetch.an.amendements import fetch_and_parse_all

    responses.add(
        responses.GET,
        build_url(14, 4072),
        body=read_sample_data("an_liste.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(14, 4072, 177),
        body=read_sample_data("an_177.xml"),
        status=200,
    )
    responses.add(responses.GET, build_url(14, 4072, 270), status=404)
    responses.add(
        responses.GET,
        build_url(14, 4072, 723),
        body=read_sample_data("an_723.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(14, 4072, 135),
        body=read_sample_data("an_135.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(14, 4072, 192),
        body=read_sample_data("an_192.xml"),
        status=200,
    )

    title, amendements, errored = fetch_and_parse_all(
        legislature=14, texte=4072, organe="PO717460", groups_folder=SAMPLE_DATA_DIR
    )

    assert title == "PLFSS 2017"
    assert len(amendements) == 4
    assert amendements[0].num == 177
    assert amendements[1].num == 723
    assert amendements[2].num == 135
    assert amendements[3].num == 192

    assert [amdt.position for amdt in amendements] == list(range(1, 5))
    assert errored == ["270"]


@responses.activate
def test_fetch_amendements():
    from zam_repondeur.fetch.an.amendements import fetch_amendements

    responses.add(
        responses.GET,
        build_url(14, 4072),
        body=read_sample_data("an_liste.xml"),
        status=200,
    )

    title, items = fetch_amendements(
        legislature=14, texte=4072, organe="PO717460", groups_folder=SAMPLE_DATA_DIR
    )

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
    from zam_repondeur.fetch.an.amendements import fetch_amendements, NotFound

    responses.add(responses.GET, build_url(14, 4072), status=404)

    with pytest.raises(NotFound):
        fetch_amendements(
            legislature=14, texte=4072, organe="PO717460", groups_folder=SAMPLE_DATA_DIR
        )


@responses.activate
def test_fetch_amendement():
    from zam_repondeur.fetch.an.amendements import fetch_amendement
    from zam_aspirateur.amendements.models import Amendement

    responses.add(
        responses.GET,
        build_url(14, 4072, 177),
        body=read_sample_data("an_177.xml"),
        status=200,
    )

    amendement = fetch_amendement(
        legislature=14,
        texte=4072,
        numero=177,
        organe="PO717460",
        groups_folder=SAMPLE_DATA_DIR,
        position=1,
    )

    assert amendement == Amendement(
        chambre="an",
        session="14",
        num_texte=4072,
        organe="PO717460",
        subdiv_type="article",
        subdiv_num="3",
        subdiv_mult="",
        subdiv_pos="",
        alinea="",
        num=177,
        rectif=0,
        auteur="Door Jean-Pierre",
        matricule="267289",
        groupe="Les Républicains",
        date_depot=None,
        sort="rejeté",
        position=1,
        discussion_commune=None,
        identique=None,
        dispositif="<p>Supprimer cet article.</p>",
        objet="<p>Amendement d&#8217;appel.</p>\n<p>Pour couvrir les d&#233;passements attendus de l&#8217;ONDAM pour 2016, cet article pr&#233;voit un pr&#233;l&#232;vement de 200 millions d&#8217;&#8364; sur les fonds de roulement de l&#8217;association nationale pour la formation permanente du personnel hospitalier (ANFH) et du fonds pour l&#8217;emploi hospitalier (FEH) pour financer le <span>fonds pour la modernisation des &#233;tablissements de sant&#233; publics et priv&#233;s</span>(FMESPP) en remplacement de cr&#233;dit de l&#8217;ONDAM. Il participe donc &#224; la pr&#233;sentation insinc&#232;re de la construction de l&#8217;ONDAM, d&#233;nonc&#233;e par le Comit&#233; d&#8217;alerte le 12 octobre dernier.</p>",  # noqa
        resume=None,
        avis=None,
        observations=None,
        reponse=None,
    )


@responses.activate
def test_fetch_amendement_gouvernement():
    from zam_repondeur.fetch.an.amendements import fetch_amendement

    responses.add(
        responses.GET,
        build_url(14, 4072, 723),
        body=read_sample_data("an_723.xml"),
        status=200,
    )

    amendement = fetch_amendement(
        legislature=14,
        texte=4072,
        numero=723,
        organe="PO717460",
        groups_folder=SAMPLE_DATA_DIR,
        position=1,
    )

    assert amendement.gouvernemental is True
    assert amendement.groupe == ""


@responses.activate
def test_fetch_amendement_commission():
    from zam_repondeur.fetch.an.amendements import fetch_amendement

    responses.add(
        responses.GET,
        build_url(14, 4072, 135),
        body=read_sample_data("an_135.xml"),
        status=200,
    )

    amendement = fetch_amendement(
        legislature=14,
        texte=4072,
        numero=135,
        organe="PO717460",
        groups_folder=SAMPLE_DATA_DIR,
        position=1,
    )

    assert amendement.gouvernemental is False
    assert amendement.auteur == "Bapt Gérard"
    assert amendement.groupe == ""


@responses.activate
def test_fetch_amendement_sort_nil():
    from zam_repondeur.fetch.an.amendements import fetch_amendement

    responses.add(
        responses.GET,
        build_url(14, 4072, 38),
        body=read_sample_data("an_38.xml"),
        status=200,
    )

    amendement = fetch_amendement(
        legislature=14,
        texte=4072,
        numero=38,
        organe="PO717460",
        groups_folder=SAMPLE_DATA_DIR,
        position=1,
    )

    assert amendement.sort == ""


@responses.activate
def test_fetch_amendement_apres():
    from zam_repondeur.fetch.an.amendements import fetch_amendement

    responses.add(
        responses.GET,
        build_url(14, 4072, 192),
        body=read_sample_data("an_192.xml"),
        status=200,
    )

    amendement = fetch_amendement(
        legislature=14,
        texte=4072,
        numero=192,
        organe="PO717460",
        groups_folder=SAMPLE_DATA_DIR,
        position=1,
    )

    assert amendement.subdiv_type == "article"
    assert amendement.subdiv_num == "8"
    assert amendement.subdiv_mult == ""
    assert amendement.subdiv_pos == "apres"


@responses.activate
def test_fetch_amendement_not_found():
    from zam_repondeur.fetch.an.amendements import fetch_amendement, NotFound

    responses.add(responses.GET, build_url(14, 4072, 177), status=404)

    with pytest.raises(NotFound):
        fetch_amendement(
            legislature=14,
            texte=4072,
            numero=177,
            organe="PO717460",
            groups_folder=SAMPLE_DATA_DIR,
            position=1,
        )


@pytest.mark.parametrize(
    "division,type_,num,mult,pos",
    [
        (
            {
                "titre": "pour un État au service d’une société de confiance.",
                "divisionDesignation": "TITRE",
                "type": "TITRE",
                "avantApres": "A",
                "divisionRattache": "TITRE",
                "articleAdditionnel": {
                    "@xsi:nil": "true",
                    "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                },
                "divisionAdditionnelle": {
                    "@xsi:nil": "true",
                    "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                },
                "urlDivisionTexteVise": "/15/textes/0575.asp#D_pour_un_Etat_au_service_dune_societe_d",  # noqa
            },
            "titre",
            "",
            "",
            "",
        )
    ],
)
def test_parse_division(division, type_, num, mult, pos):
    from zam_repondeur.fetch.an.amendements import parse_division

    assert parse_division(division) == (type_, num, mult, pos)
