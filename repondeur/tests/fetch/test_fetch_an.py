from pathlib import Path

import pytest
import responses

from zam_repondeur.fetch.an.amendements import build_url

HERE = Path(__file__)
SAMPLE_DATA_DIR = HERE.parent / "sample_data"


def read_sample_data(basename):
    return (SAMPLE_DATA_DIR / basename).read_text()


@responses.activate
def test_fetch_and_parse_all(lecture_an):
    from zam_repondeur.fetch.an.amendements import fetch_and_parse_all

    responses.add(
        responses.GET,
        build_url(15, 269),
        body=read_sample_data("an_liste.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 177),
        body=read_sample_data("an_177.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 270),
        body=read_sample_data("an_270.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 723),
        body=read_sample_data("an_723.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 135),
        body=read_sample_data("an_135.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 192),
        body=read_sample_data("an_192.xml"),
        status=200,
    )

    amendements, created, errored = fetch_and_parse_all(lecture=lecture_an)

    assert len(amendements) == 5
    assert amendements[0].num == 177
    assert amendements[1].num == 270
    assert amendements[2].num == 723
    assert amendements[3].num == 135
    assert amendements[4].num == 192

    assert [amdt.position for amdt in amendements] == list(range(1, 6))
    assert created == 5
    assert errored == []


@responses.activate
def test_fetch_and_parse_all_with_404(lecture_an):
    from zam_repondeur.fetch.an.amendements import fetch_and_parse_all

    responses.add(
        responses.GET,
        build_url(15, 269),
        body=read_sample_data("an_liste.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 177),
        body=read_sample_data("an_177.xml"),
        status=200,
    )
    responses.add(responses.GET, build_url(15, 269, 270), status=404)
    responses.add(
        responses.GET,
        build_url(15, 269, 723),
        body=read_sample_data("an_723.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 135),
        body=read_sample_data("an_135.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 192),
        body=read_sample_data("an_192.xml"),
        status=200,
    )

    amendements, created, errored = fetch_and_parse_all(lecture=lecture_an)

    assert len(amendements) == 4
    assert amendements[0].num == 177
    assert amendements[1].num == 723
    assert amendements[2].num == 135
    assert amendements[3].num == 192

    assert [amdt.position for amdt in amendements] == list(range(1, 5))
    assert created == 4
    assert errored == ["270"]


@responses.activate
def test_fetch_amendements(lecture_an):
    from zam_repondeur.fetch.an.amendements import fetch_amendements

    responses.add(
        responses.GET,
        build_url(15, 269),
        body=read_sample_data("an_liste.xml"),
        status=200,
    )

    items = fetch_amendements(lecture=lecture_an)

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
def test_fetch_amendements_not_found(lecture_an):
    from zam_repondeur.fetch.an.amendements import fetch_amendements, NotFound

    responses.add(responses.GET, build_url(15, 269), status=404)

    with pytest.raises(NotFound):
        fetch_amendements(lecture=lecture_an)


@responses.activate
def test_fetch_amendement(app, lecture_an):
    from zam_repondeur.fetch.an.amendements import fetch_amendement

    responses.add(
        responses.GET,
        build_url(15, 269, 177),
        body=read_sample_data("an_177.xml"),
        status=200,
    )

    amendement, created = fetch_amendement(lecture=lecture_an, numero=177, position=1)

    assert amendement.lecture == lecture_an
    assert amendement.num == 177
    assert amendement.rectif == 0
    assert amendement.auteur == "Door Jean-Pierre"
    assert amendement.matricule == "267289"
    assert amendement.date_depot is None
    assert amendement.sort == "rejeté"
    assert amendement.position == 1
    assert amendement.discussion_commune is None
    assert amendement.identique is None
    assert amendement.parent is None
    assert amendement.dispositif == "<p>Supprimer cet article.</p>"
    assert amendement.objet == (
        "<p>Amendement d&#8217;appel.</p>\n<p>Pour couvrir les d&#233;passements "
        "attendus de l&#8217;ONDAM pour 2016, cet article pr&#233;voit un "
        "pr&#233;l&#232;vement de 200 millions d&#8217;&#8364; sur les fonds de "
        "roulement de l&#8217;association nationale pour la formation permanente du "
        "personnel hospitalier (ANFH) et du fonds pour l&#8217;emploi hospitalier "
        "(FEH) pour financer le <span>fonds pour la modernisation des "
        "&#233;tablissements de sant&#233; publics et priv&#233;s</span>(FMESPP) en "
        "remplacement de cr&#233;dit de l&#8217;ONDAM. Il participe donc &#224; la "
        "pr&#233;sentation insinc&#232;re de la construction de l&#8217;ONDAM, "
        "d&#233;nonc&#233;e par le Comit&#233; d&#8217;alerte le 12 octobre dernier."
        "</p>"
    )
    assert amendement.resume is None
    assert amendement.avis is None
    assert amendement.observations is None
    assert amendement.reponse is None


@responses.activate
def test_fetch_amendement_gouvernement(lecture_an):
    from zam_repondeur.fetch.an.amendements import fetch_amendement

    responses.add(
        responses.GET,
        build_url(15, 269, 723),
        body=read_sample_data("an_723.xml"),
        status=200,
    )

    amendement, created = fetch_amendement(lecture=lecture_an, numero=723, position=1)

    assert amendement.gouvernemental is True
    assert amendement.groupe == ""


@responses.activate
def test_fetch_amendement_commission(lecture_an):
    from zam_repondeur.fetch.an.amendements import fetch_amendement

    responses.add(
        responses.GET,
        build_url(15, 269, 135),
        body=read_sample_data("an_135.xml"),
        status=200,
    )

    amendement, created = fetch_amendement(lecture=lecture_an, numero=135, position=1)

    assert amendement.gouvernemental is False
    assert amendement.auteur == "Bapt Gérard"
    assert amendement.groupe == ""


@responses.activate
def test_fetch_sous_amendement(app, lecture_an):
    from zam_repondeur.fetch.an.amendements import fetch_amendement

    responses.add(
        responses.GET,
        build_url(15, 269, 941),
        body=read_sample_data("an_941.xml"),
        status=200,
    )

    amendement, created = fetch_amendement(lecture=lecture_an, numero=941, position=1)

    assert amendement.parent.num == 155


@responses.activate
def test_fetch_amendement_sort_nil(lecture_an):
    from zam_repondeur.fetch.an.amendements import fetch_amendement

    responses.add(
        responses.GET,
        build_url(15, 269, 38),
        body=read_sample_data("an_38.xml"),
        status=200,
    )

    amendement, created = fetch_amendement(lecture=lecture_an, numero=38, position=1)

    assert amendement.sort == ""


@responses.activate
def test_fetch_amendement_apres(lecture_an):
    from zam_repondeur.fetch.an.amendements import fetch_amendement

    responses.add(
        responses.GET,
        build_url(15, 269, 192),
        body=read_sample_data("an_192.xml"),
        status=200,
    )

    amendement, created = fetch_amendement(lecture=lecture_an, numero=192, position=1)

    assert amendement.article.type == "article"
    assert amendement.article.num == "8"
    assert amendement.article.mult == ""
    assert amendement.article.pos == "apres"


@responses.activate
def test_fetch_amendement_not_found(lecture_an):
    from zam_repondeur.fetch.an.amendements import fetch_amendement, NotFound

    responses.add(responses.GET, build_url(15, 269, 177), status=404)

    with pytest.raises(NotFound):
        fetch_amendement(lecture=lecture_an, numero=177, position=1)


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
