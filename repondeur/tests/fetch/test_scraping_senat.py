from pathlib import Path

import responses


@responses.activate
def test_get_dossiers_senat():
    from zam_repondeur.fetch.an.dossiers.models import DossierRef
    from zam_repondeur.fetch.senat.scraping import get_dossiers_senat

    pids = {
        "ppl18-462",
        "ppl18-260",
        "ppl18-385",
        "ppl18-043",
        "pjl18-532",
        "ppl18-002",
        "ppl18-229",
        "pjl18-404",
        "pjl18-523",
        "ppl18-305",
        "ppr18-458",
        "pjl18-526",
        "ppl18-386",
        "ppl18-454",
        "ppl17-699",
        "ppl18-436",
    }
    responses.add(
        responses.GET,
        f"http://www.senat.fr/dossiers-legislatifs/textes-recents.html",
        body=(
            Path(__file__).parent / "sample_data" / "senat" / "textes-recents.html"
        ).read_text("utf-8", "ignore"),
        status=200,
    )
    for pid in pids:
        responses.add(
            responses.GET,
            f"http://www.senat.fr/dossier-legislatif/rss/dosleg{pid}.xml",
            body=(Path(__file__).parent / "sample_data" / "senat" / f"dosleg{pid}.xml")
            .read_text("utf-8")
            .encode("latin-1"),
            status=200,
        )
    assert set(get_dossiers_senat().keys()) == pids
    assert (
        DossierRef(
            uid="ppl18-385",
            titre="Clarifier diverses dispositions du droit électoral",
            lectures=[],
        )
        in get_dossiers_senat().values()
    )
    assert (
        DossierRef(
            uid="pjl18-404", titre="Organisation du système de santé", lectures=[]
        )
        in get_dossiers_senat().values()
    )
    assert (
        DossierRef(
            uid="ppl18-462",
            titre="Participation des conseillers de Lyon aux élections sénatoriales",
            lectures=[],
        )
        in get_dossiers_senat().values()
    )
    assert (
        DossierRef(
            uid="ppl18-043",
            titre=(
                "Directeur général de l'Agence nationale de la cohésion des territoires"
            ),
            lectures=[],
        )
        in get_dossiers_senat().values()
    )
    assert (
        DossierRef(
            uid="ppl18-454",
            titre="Exploitation des réseaux radioélectriques mobiles",
            lectures=[],
        )
        in get_dossiers_senat().values()
    )
    assert (
        DossierRef(
            uid="pjl18-526",
            titre="Accords France-Suisse et France-Luxembourg",
            lectures=[],
        )
        in get_dossiers_senat().values()
    )
    assert (
        DossierRef(
            uid="ppl17-699",
            titre="Instituer un médiateur territorial dans certaines collectivités",
            lectures=[],
        )
        in get_dossiers_senat().values()
    )
    assert (
        DossierRef(
            uid="ppl18-305", titre="Création d'un statut de l'élu communal", lectures=[]
        )
        in get_dossiers_senat().values()
    )
    assert (
        DossierRef(
            uid="ppl18-436", titre="Accès des PME à la commande publique", lectures=[]
        )
        in get_dossiers_senat().values()
    )
    assert (
        DossierRef(
            uid="ppr18-458",
            titre="Clarifier et actualiser le Règlement du Sénat",
            lectures=[],
        )
        in get_dossiers_senat().values()
    )
    assert (
        DossierRef(
            uid="ppl18-260",
            titre="Accès à l'énergie et lutte contre la précarité énergétique",
            lectures=[],
        )
        in get_dossiers_senat().values()
    )
    assert (
        DossierRef(
            uid="pjl18-532", titre="Transformation de la fonction publique", lectures=[]
        )
        in get_dossiers_senat().values()
    )
    assert (
        DossierRef(
            uid="ppl18-229",
            titre="Lutte contre l'habitat insalubre ou dangereux",
            lectures=[],
        )
        in get_dossiers_senat().values()
    )
    assert (
        DossierRef(uid="pjl18-523", titre="Accord France Arménie", lectures=[])
        in get_dossiers_senat().values()
    )
    assert (
        DossierRef(
            uid="ppl18-386",
            titre="Clarifier diverses dispositions du droit électoral",
            lectures=[],
        )
        in get_dossiers_senat().values()
    )
    assert (
        DossierRef(
            uid="ppl18-002",
            titre="Agence nationale de la cohésion des territoires",
            lectures=[],
        )
        in get_dossiers_senat().values()
    )


def test_extract_recent_urls():
    from zam_repondeur.fetch.senat.scraping import (
        download_textes_recents,
        extract_recent_urls,
    )

    assert extract_recent_urls(download_textes_recents()) == {
        "/dossier-legislatif/pjl18-404.html",
        "/dossier-legislatif/pjl18-523.html",
        "/dossier-legislatif/pjl18-526.html",
        "/dossier-legislatif/pjl18-532.html",
        "/dossier-legislatif/ppl17-699.html",
        "/dossier-legislatif/ppl18-002.html",
        "/dossier-legislatif/ppl18-043.html",
        "/dossier-legislatif/ppl18-229.html",
        "/dossier-legislatif/ppl18-260.html",
        "/dossier-legislatif/ppl18-305.html",
        "/dossier-legislatif/ppl18-385.html",
        "/dossier-legislatif/ppl18-386.html",
        "/dossier-legislatif/ppl18-436.html",
        "/dossier-legislatif/ppl18-454.html",
        "/dossier-legislatif/ppl18-462.html",
        "/dossier-legislatif/ppr18-458.html",
    }


def test_convert_to_rss_urls():
    from zam_repondeur.fetch.senat.scraping import (
        download_textes_recents,
        extract_recent_urls,
        convert_to_rss_urls,
    )

    assert convert_to_rss_urls(extract_recent_urls(download_textes_recents())) == {
        "pjl18-404": "/dossier-legislatif/rss/doslegpjl18-404.xml",
        "pjl18-523": "/dossier-legislatif/rss/doslegpjl18-523.xml",
        "pjl18-526": "/dossier-legislatif/rss/doslegpjl18-526.xml",
        "pjl18-532": "/dossier-legislatif/rss/doslegpjl18-532.xml",
        "ppl17-699": "/dossier-legislatif/rss/doslegppl17-699.xml",
        "ppl18-002": "/dossier-legislatif/rss/doslegppl18-002.xml",
        "ppl18-043": "/dossier-legislatif/rss/doslegppl18-043.xml",
        "ppl18-229": "/dossier-legislatif/rss/doslegppl18-229.xml",
        "ppl18-260": "/dossier-legislatif/rss/doslegppl18-260.xml",
        "ppl18-305": "/dossier-legislatif/rss/doslegppl18-305.xml",
        "ppl18-385": "/dossier-legislatif/rss/doslegppl18-385.xml",
        "ppl18-386": "/dossier-legislatif/rss/doslegppl18-386.xml",
        "ppl18-436": "/dossier-legislatif/rss/doslegppl18-436.xml",
        "ppl18-454": "/dossier-legislatif/rss/doslegppl18-454.xml",
        "ppl18-462": "/dossier-legislatif/rss/doslegppl18-462.xml",
        "ppr18-458": "/dossier-legislatif/rss/doslegppr18-458.xml",
    }


@responses.activate
def test_create_dossier():
    from zam_repondeur.fetch.an.dossiers.models import DossierRef
    from zam_repondeur.fetch.senat.scraping import create_dossier

    responses.add(
        responses.GET,
        "http://www.senat.fr/dossier-legislatif/rss/doslegpjl18-404.xml",
        body=(Path(__file__).parent / "sample_data" / "senat" / "doslegpjl18-404.xml")
        .read_text("utf-8")
        .encode("latin-1"),
        status=200,
    )
    assert create_dossier(
        "pjl18-404", "/dossier-legislatif/rss/doslegpjl18-404.xml"
    ) == DossierRef(
        uid="pjl18-404", titre="Organisation du système de santé", lectures=[]
    )
