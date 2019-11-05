class TestMatchDossierRef:
    def test_match_with_an_url_alt(self):
        from zam_repondeur.services.fetch.an.dossiers.models import DossierRef

        dossier_an = DossierRef(
            uid="DLR5L15N37702",
            titre="Violences au sein des familles",
            slug="violences-faites-femmes",
            an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/Violences_faites_aux_femmes",  # noqa
            senat_url="",
            lectures=[],
        )
        dossier_senat = DossierRef(
            uid="ppl19-057",
            titre="Agir contre les violences au sein de la famille",
            slug="",
            an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/Violences_faites_aux_femmes",  # noqa
            senat_url="https://www.senat.fr/dossier-legislatif/ppl19-057.html",
            lectures=[],
        )
        assert dossier_an.matches(dossier_senat)
        assert dossier_senat.matches(dossier_an)

    def test_match_with_senat_url_https(self):
        from zam_repondeur.services.fetch.an.dossiers.models import DossierRef

        dossier_an = DossierRef(
            uid="DLR5L15N36030",
            titre="Loi de financement de la sécurité sociale 2019",
            slug="plfss_2019",
            an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/plfss_2019",
            senat_url="http://www.senat.fr/dossier-legislatif/plfss2019.html",
            lectures=[],
        )
        dossier_senat = DossierRef(
            uid="plfss2019",
            titre="Financement de la sécurité sociale pour 2019",
            slug="plfss_2019",
            an_url="http://www.assemblee-nationale.fr/15/dossiers/plfss_2019.asp",
            senat_url="https://www.senat.fr/dossier-legislatif/plfss2019.html",
            lectures=[],
        )
        assert dossier_an.matches(dossier_senat)
        assert dossier_senat.matches(dossier_an)
