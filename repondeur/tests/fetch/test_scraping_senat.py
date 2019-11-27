import datetime


def test_get_dossier_refs_senat():
    from zam_repondeur.services.fetch.senat.scraping import get_dossier_refs_senat

    dossiers = get_dossier_refs_senat()

    assert set(dossiers.keys()) == {
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


def test_extract_recent_urls():
    from zam_repondeur.services.fetch.senat.scraping import (
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


def test_convert_to_rss_url():
    from zam_repondeur.services.fetch.senat.scraping import (
        build_rss_url,
        download_textes_recents,
        extract_dossier_id,
        extract_recent_urls,
    )

    webpages_urls = extract_recent_urls(download_textes_recents())
    dossier_ids = (extract_dossier_id(url) for url in webpages_urls)
    rss_urls = {dossier_id: build_rss_url(dossier_id) for dossier_id in dossier_ids}

    assert rss_urls == {
        "pjl18-404": "https://www.senat.fr/dossier-legislatif/rss/doslegpjl18-404.xml",
        "pjl18-523": "https://www.senat.fr/dossier-legislatif/rss/doslegpjl18-523.xml",
        "pjl18-526": "https://www.senat.fr/dossier-legislatif/rss/doslegpjl18-526.xml",
        "pjl18-532": "https://www.senat.fr/dossier-legislatif/rss/doslegpjl18-532.xml",
        "ppl17-699": "https://www.senat.fr/dossier-legislatif/rss/doslegppl17-699.xml",
        "ppl18-002": "https://www.senat.fr/dossier-legislatif/rss/doslegppl18-002.xml",
        "ppl18-043": "https://www.senat.fr/dossier-legislatif/rss/doslegppl18-043.xml",
        "ppl18-229": "https://www.senat.fr/dossier-legislatif/rss/doslegppl18-229.xml",
        "ppl18-260": "https://www.senat.fr/dossier-legislatif/rss/doslegppl18-260.xml",
        "ppl18-305": "https://www.senat.fr/dossier-legislatif/rss/doslegppl18-305.xml",
        "ppl18-385": "https://www.senat.fr/dossier-legislatif/rss/doslegppl18-385.xml",
        "ppl18-386": "https://www.senat.fr/dossier-legislatif/rss/doslegppl18-386.xml",
        "ppl18-436": "https://www.senat.fr/dossier-legislatif/rss/doslegppl18-436.xml",
        "ppl18-454": "https://www.senat.fr/dossier-legislatif/rss/doslegppl18-454.xml",
        "ppl18-462": "https://www.senat.fr/dossier-legislatif/rss/doslegppl18-462.xml",
        "ppr18-458": "https://www.senat.fr/dossier-legislatif/rss/doslegppr18-458.xml",
    }


class TestCreateDossierRef:
    def test_pjl18_404(self):
        """
        Simple case: commission, then séance publique on adopted text
        """
        from zam_repondeur.services.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.services.fetch.senat.scraping import create_dossier_ref
        from zam_repondeur.models.chambre import Chambre
        from zam_repondeur.models.phase import Phase

        assert create_dossier_ref("pjl18-404") == DossierRef(
            uid="pjl18-404",
            titre="Organisation du système de santé",
            slug="organisation-systeme-sante",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/pjl18-404.html",
            lectures=[
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Commissions",
                    texte=TexteRef(
                        uid="PJLSENAT2019X404",
                        type_=TypeTexte.PROJET,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=404,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 3, 26),
                    ),
                    organe="",  # commission X
                    partie=None,
                ),
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PJLSENAT2019X525",
                        type_=TypeTexte.PROJET,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=525,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 5, 22),
                    ),
                    organe="PO78718",  # séance publique
                    partie=None,
                ),
            ],
        )

    def test_pjl18_523(self):
        """
        Simple case: commission, then séance publique on adopted text
        """
        from zam_repondeur.services.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.services.fetch.senat.scraping import create_dossier_ref
        from zam_repondeur.models.chambre import Chambre
        from zam_repondeur.models.phase import Phase

        assert create_dossier_ref("pjl18-523") == DossierRef(
            uid="pjl18-523",
            titre="Accord France Arménie",
            slug="accord-france-armenie",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/pjl18-523.html",
            lectures=[
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Commissions",
                    texte=TexteRef(
                        uid="PJLSENAT2019X523",
                        type_=TypeTexte.PROJET,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=523,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 5, 22),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PJLSENAT2019X565",
                        type_=TypeTexte.PROJET,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=565,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 6, 12),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        )

    def test_pjl18_526(self):
        """
        Simple case: commission, then séance publique on adopted text
        """
        from zam_repondeur.services.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.services.fetch.senat.scraping import create_dossier_ref
        from zam_repondeur.models.chambre import Chambre
        from zam_repondeur.models.phase import Phase

        assert create_dossier_ref("pjl18-526") == DossierRef(
            uid="pjl18-526",
            titre="Accords France-Suisse et France-Luxembourg",
            slug="accords-france-suisse-france-luxembourg",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/pjl18-526.html",
            lectures=[
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Commissions",
                    texte=TexteRef(
                        uid="PJLSENAT2019X526",
                        type_=TypeTexte.PROJET,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=526,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 5, 24),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PJLSENAT2019X567",
                        type_=TypeTexte.PROJET,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=567,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 6, 12),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        )

    def test_pjl18_532(self):
        """
        Simple case: commission, then séance publique on adopted text
        """
        from zam_repondeur.services.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.services.fetch.senat.scraping import create_dossier_ref
        from zam_repondeur.models.chambre import Chambre
        from zam_repondeur.models.phase import Phase

        assert create_dossier_ref("pjl18-532") == DossierRef(
            uid="pjl18-532",
            titre="Transformation de la fonction publique",
            slug="transformation-fonction-publique",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/pjl18-532.html",
            lectures=[
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Commissions",
                    texte=TexteRef(
                        uid="PJLSENAT2019X532",
                        type_=TypeTexte.PROJET,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=532,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 5, 29),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PJLSENAT2019X571",
                        type_=TypeTexte.PROJET,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=571,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 6, 12),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        )

    def test_ppl17_699(self):
        """
        Simple case: commission, then séance publique on adopted text
        """
        from zam_repondeur.services.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.services.fetch.senat.scraping import create_dossier_ref
        from zam_repondeur.models.chambre import Chambre
        from zam_repondeur.models.phase import Phase

        assert create_dossier_ref("ppl17-699") == DossierRef(
            uid="ppl17-699",
            titre="Instituer un médiateur territorial dans certaines collectivités",
            slug="instituer-mediateur-territorial-certaines-collectivites",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl17-699.html",
            lectures=[
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Commissions",
                    texte=TexteRef(
                        uid="PPLSENAT2018X699",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=699,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2018, 7, 30),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2019X547",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=547,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 6, 5),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        )

    def test_ppl18_002(self):
        """
        Première & nouvelle lecture
        """
        from zam_repondeur.services.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.services.fetch.senat.scraping import create_dossier_ref
        from zam_repondeur.models.chambre import Chambre
        from zam_repondeur.models.phase import Phase

        assert create_dossier_ref("ppl18-002") == DossierRef(
            uid="ppl18-002",
            titre="Agence nationale de la cohésion des territoires",
            slug="agence-nationale-cohesion-territoires",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl18-002.html",
            lectures=[
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Commissions",
                    texte=TexteRef(
                        uid="PPLSENAT2018X2",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=2,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2018, 10, 2),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2018X99",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=99,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2018, 10, 31),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
                LectureRef(
                    phase=Phase.NOUVELLE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Nouvelle lecture – Commissions",
                    texte=TexteRef(
                        uid="PPLSENAT2019X518",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=518,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 5, 21),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    phase=Phase.NOUVELLE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Nouvelle lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2019X562",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=562,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 6, 12),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        )

    def test_ppl18_043(self):
        """
        Première & nouvelle lecture
        """
        from zam_repondeur.services.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.services.fetch.senat.scraping import create_dossier_ref
        from zam_repondeur.models.chambre import Chambre
        from zam_repondeur.models.phase import Phase

        assert create_dossier_ref("ppl18-043") == DossierRef(
            uid="ppl18-043",
            titre="Directeur général de l'Agence nationale de la cohésion des territoires",  # noqa
            slug="directeur-general-agence-nationale-cohesion-territoires",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl18-043.html",
            lectures=[
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Commissions",
                    texte=TexteRef(
                        uid="PPLSENAT2018X43",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=43,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2018, 10, 16),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2018X100",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=100,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2018, 10, 31),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        )

    def test_ppl18_229(self):
        """
        This one is tricky: renvoi en commission après séance publique

        There are two séance publique 1re lecture:
        - one on the initial texte
        - one on the new texte voted by the commission the 2nd time

        There are actually 2 commission lectures on the same initial texte,
        but with different URLs for amendements:
        - http://www.senat.fr/amendements/commissions/2018-2019/10229/liste_depot.html
        - http://www.senat.fr/amendements/commissions/2018-2019/229/liste_depot.html

        Looks like they created a fake texte with number 10229.

        TODO: find a way to represent both commission lectures.
        """
        from zam_repondeur.services.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.services.fetch.senat.scraping import create_dossier_ref
        from zam_repondeur.models.chambre import Chambre
        from zam_repondeur.models.phase import Phase

        assert create_dossier_ref("ppl18-229") == DossierRef(
            uid="ppl18-229",
            titre="Lutte contre l'habitat insalubre ou dangereux",
            slug="lutte-contre-habitat-insalubre-ou-dangereux",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl18-229.html",
            lectures=[
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Commissions",
                    texte=TexteRef(
                        uid="PPLSENAT2018X229",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=229,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2018, 12, 20),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2018X229",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=229,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2018, 12, 20),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2019X536",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=536,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 5, 29),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        )

    def test_ppl18_260(self):
        """
        Commission does not vote a new texte
        """
        from zam_repondeur.services.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.services.fetch.senat.scraping import create_dossier_ref
        from zam_repondeur.models.chambre import Chambre
        from zam_repondeur.models.phase import Phase

        assert create_dossier_ref("ppl18-260") == DossierRef(
            uid="ppl18-260",
            titre="Accès à l'énergie et lutte contre la précarité énergétique",
            slug="acces-energie-lutte-contre-precarite-energetique",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl18-260.html",
            lectures=[
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Commissions",
                    texte=TexteRef(
                        uid="PPLSENAT2019X260",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=260,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 1, 22),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2019X260",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=260,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 1, 22),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        )

    def test_ppl18_305(self):
        """
        Commission does not vote a new texte
        """
        from zam_repondeur.services.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.services.fetch.senat.scraping import create_dossier_ref
        from zam_repondeur.models.chambre import Chambre
        from zam_repondeur.models.phase import Phase

        assert create_dossier_ref("ppl18-305") == DossierRef(
            uid="ppl18-305",
            titre="Création d'un statut de l'élu communal",
            slug="creation-statut-elu-communal",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl18-305.html",
            lectures=[
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Commissions",
                    texte=TexteRef(
                        uid="PPLSENAT2019X305",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=305,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 2, 12),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2019X305",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=305,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 2, 12),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        )

    def test_ppl18_385(self):
        """
        Simple case: commission, then séance publique on adopted text
        """
        from zam_repondeur.services.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.services.fetch.senat.scraping import create_dossier_ref
        from zam_repondeur.models.chambre import Chambre
        from zam_repondeur.models.phase import Phase

        assert create_dossier_ref("ppl18-385") == DossierRef(
            uid="ppl18-385",
            titre="Clarifier diverses dispositions du droit électoral",
            slug="clarifier-diverses-dispositions-droit-electoral",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl18-385.html",
            lectures=[
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Commissions",
                    texte=TexteRef(
                        uid="PPLSENAT2019X385",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=385,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 3, 19),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2019X444",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=444,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 4, 10),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        )

    def test_ppl18_386(self):
        """
        Simple case: commission, then séance publique on adopted text
        """
        from zam_repondeur.services.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.services.fetch.senat.scraping import create_dossier_ref
        from zam_repondeur.models.chambre import Chambre
        from zam_repondeur.models.phase import Phase

        assert create_dossier_ref("ppl18-386") == DossierRef(
            uid="ppl18-386",
            titre="Clarifier diverses dispositions du droit électoral",
            slug="clarifier-diverses-dispositions-droit-electoral",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl18-386.html",
            lectures=[
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Commissions",
                    texte=TexteRef(
                        uid="PPLSENAT2019X386",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=386,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 3, 19),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2019X445",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=445,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 4, 10),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        )

    def test_ppl18_436(self):
        """
        Commission does not vote a new texte
        """
        from zam_repondeur.services.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.services.fetch.senat.scraping import create_dossier_ref
        from zam_repondeur.models.chambre import Chambre
        from zam_repondeur.models.phase import Phase

        assert create_dossier_ref("ppl18-436") == DossierRef(
            uid="ppl18-436",
            titre="Accès des PME à la commande publique",
            slug="acces-pme-commande-publique",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl18-436.html",
            lectures=[
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Commissions",
                    texte=TexteRef(
                        uid="PPLSENAT2019X436",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=436,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 4, 4),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2019X436",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=436,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 4, 4),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        )

    def test_ppl18_454(self):
        """
        Commission has not adopted a new texte yet
        """
        from zam_repondeur.services.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.services.fetch.senat.scraping import create_dossier_ref
        from zam_repondeur.models.chambre import Chambre
        from zam_repondeur.models.phase import Phase

        assert create_dossier_ref("ppl18-454") == DossierRef(
            uid="ppl18-454",
            titre="Exploitation des réseaux radioélectriques mobiles",
            slug="exploitation-reseaux-radioelectriques-mobiles",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl18-454.html",
            lectures=[
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Commissions",
                    texte=TexteRef(
                        uid="PPLSENAT2019X454",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=454,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 4, 11),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2019X454",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=454,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 4, 11),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        )

    def test_ppl18_462(self):
        """
        Simple case: commission, then séance publique on adopted text
        """
        from zam_repondeur.services.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.services.fetch.senat.scraping import create_dossier_ref
        from zam_repondeur.models.chambre import Chambre
        from zam_repondeur.models.phase import Phase

        assert create_dossier_ref("ppl18-462") == DossierRef(
            uid="ppl18-462",
            titre="Participation des conseillers de Lyon aux élections sénatoriales",
            slug="participation-conseillers-lyon-elections-senatoriales",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl18-462.html",
            lectures=[
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Commissions",
                    texte=TexteRef(
                        uid="PPLSENAT2019X462",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=462,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 4, 16),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2019X552",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=552,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 6, 5),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        )

    def test_ppr18_458(self):
        """
        Résolution: the government is most likely not involved
        """
        from zam_repondeur.services.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.services.fetch.senat.scraping import create_dossier_ref
        from zam_repondeur.models.chambre import Chambre
        from zam_repondeur.models.phase import Phase

        assert create_dossier_ref("ppr18-458") == DossierRef(
            uid="ppr18-458",
            titre="Clarifier et actualiser le Règlement du Sénat",
            slug="clarifier-actualiser-reglement-senat",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppr18-458.html",
            lectures=[
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Commissions",
                    texte=TexteRef(
                        uid="PPRSENAT2019X458",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=458,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 4, 12),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    phase=Phase.PREMIERE_LECTURE,
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPRSENAT2019X550",
                        type_=TypeTexte.PROPOSITION,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=550,
                        titre_long="",
                        titre_court="",
                        date_depot=datetime.date(2019, 6, 5),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        )
