"""
Test that we take account different kind of changes when fetching updates from Sénat
"""
from pathlib import Path

import responses

from zam_repondeur.fetch.senat.amendements import aspire_senat
from zam_repondeur.models import DBSession


HERE = Path(__file__)
SAMPLE_DATA_DIR = HERE.parent / "sample_data"


def read_sample_data(basename):
    return (SAMPLE_DATA_DIR / basename).read_bytes()


@responses.activate
def test_position_changed(lecture_senat):
    """
    The discussion order of amendements may change
    """

    responses.add(
        responses.GET,
        "https://www.senat.fr/amendements/2017-2018/63/jeu_complet_2017-2018_63.csv",
        body=read_sample_data("jeu_complet_2017-2018_63-short.csv"),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv",
        body=read_sample_data("ODSEN_GENERAL-short.csv"),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://www.senat.fr/enseance/2017-2018/63/liste_discussion.json",
        body=read_sample_data("liste_discussion_63-short.json"),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://www.senat.fr/enseance/2017-2018/63/liste_discussion.json",
        body=read_sample_data("liste_discussion_63-short-position.json"),
        status=200,
    )

    DBSession.add(lecture_senat)

    aspire_senat(lecture_senat)

    assert {amdt.num: amdt.position for amdt in lecture_senat.amendements} == {
        31: 1,
        443: 2,
    }

    aspire_senat(lecture_senat)

    assert {amdt.num: amdt.position for amdt in lecture_senat.amendements} == {
        31: 2,
        443: 1,
    }


@responses.activate
def test_retire_avant_seance_ou_irrecevable(lecture_senat):
    """
    An amendement that is either withdrawn by its author or declared invalid
    will be removed from the "liste_discussion"
    """

    responses.add(
        responses.GET,
        "https://www.senat.fr/amendements/2017-2018/63/jeu_complet_2017-2018_63.csv",
        body=read_sample_data("jeu_complet_2017-2018_63-short.csv"),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv",
        body=read_sample_data("ODSEN_GENERAL-short.csv"),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://www.senat.fr/enseance/2017-2018/63/liste_discussion.json",
        body=read_sample_data("liste_discussion_63-short.json"),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://www.senat.fr/enseance/2017-2018/63/liste_discussion.json",
        body=read_sample_data("liste_discussion_63-short-retire.json"),
        status=200,
    )

    DBSession.add(lecture_senat)

    aspire_senat(lecture_senat)

    assert {amdt.num: amdt.position for amdt in lecture_senat.amendements} == {
        31: 1,
        443: 2,
    }

    aspire_senat(lecture_senat)

    assert {amdt.num: amdt.position for amdt in lecture_senat.amendements} == {
        31: 1,
        443: None,
    }


@responses.activate
def test_article_changed(lecture_senat):
    """
    The targeted article may change
    """

    responses.add(
        responses.GET,
        "https://www.senat.fr/amendements/2017-2018/63/jeu_complet_2017-2018_63.csv",
        body=read_sample_data("jeu_complet_2017-2018_63-short.csv"),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://www.senat.fr/amendements/2017-2018/63/jeu_complet_2017-2018_63.csv",
        body=read_sample_data("jeu_complet_2017-2018_63-short-article.csv"),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv",
        body=read_sample_data("ODSEN_GENERAL-short.csv"),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://www.senat.fr/enseance/2017-2018/63/liste_discussion.json",
        body=read_sample_data("liste_discussion_63-short.json"),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://www.senat.fr/enseance/2017-2018/63/liste_discussion.json",
        body=read_sample_data("liste_discussion_63-short-article.json"),
        status=200,
    )

    DBSession.add(lecture_senat)

    aspire_senat(lecture_senat)

    assert {amdt.num: str(amdt.article) for amdt in lecture_senat.amendements} == {
        31: "Art. 3",
        443: "Art. 4",
    }

    aspire_senat(lecture_senat)

    assert {amdt.num: str(amdt.article) for amdt in lecture_senat.amendements} == {
        31: "Art. 3",
        443: "Art. 3",
    }


@responses.activate
def test_add_parent_amendement(lecture_senat):
    """
    The targeted article may change
    """

    responses.add(
        responses.GET,
        "https://www.senat.fr/amendements/2017-2018/63/jeu_complet_2017-2018_63.csv",
        body=read_sample_data("jeu_complet_2017-2018_63-short.csv"),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv",
        body=read_sample_data("ODSEN_GENERAL-short.csv"),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://www.senat.fr/enseance/2017-2018/63/liste_discussion.json",
        body=read_sample_data("liste_discussion_63-short.json"),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://www.senat.fr/enseance/2017-2018/63/liste_discussion.json",
        body=read_sample_data("liste_discussion_63-short-parent.json"),
        status=200,
    )

    DBSession.add(lecture_senat)

    aspire_senat(lecture_senat)

    assert {
        amdt.num: amdt.parent.num if amdt.parent else None
        for amdt in lecture_senat.amendements
    } == {31: None, 443: None}

    aspire_senat(lecture_senat)

    assert {
        amdt.num: amdt.parent.num if amdt.parent else None
        for amdt in lecture_senat.amendements
    } == {31: None, 443: 31}


@responses.activate
def test_remove_parent_amendement(lecture_senat):
    """
    The targeted article may change
    """

    responses.add(
        responses.GET,
        "https://www.senat.fr/amendements/2017-2018/63/jeu_complet_2017-2018_63.csv",
        body=read_sample_data("jeu_complet_2017-2018_63-short.csv"),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv",
        body=read_sample_data("ODSEN_GENERAL-short.csv"),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://www.senat.fr/enseance/2017-2018/63/liste_discussion.json",
        body=read_sample_data("liste_discussion_63-short-parent.json"),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://www.senat.fr/enseance/2017-2018/63/liste_discussion.json",
        body=read_sample_data("liste_discussion_63-short.json"),
        status=200,
    )

    DBSession.add(lecture_senat)

    aspire_senat(lecture_senat)

    assert {
        amdt.num: amdt.parent.num if amdt.parent else None
        for amdt in lecture_senat.amendements
    } == {31: None, 443: 31}

    aspire_senat(lecture_senat)

    assert {
        amdt.num: amdt.parent.num if amdt.parent else None
        for amdt in lecture_senat.amendements
    } == {31: None, 443: None}
