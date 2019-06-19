from copy import deepcopy
from datetime import date


class TestMergeDossiers:
    def test_merge_empty_dossiers(self):
        from zam_repondeur.fetch.an.dossiers.models import DossierRef

        assert DossierRef.merge_dossiers({}, {}) == {}

    def test_merge_dossiers_and_empty(self):
        from zam_repondeur.fetch.an.dossiers.models import DossierRef

        dossiers1 = {"a": DossierRef("a", "titre1", "", "", [])}
        assert DossierRef.merge_dossiers(dossiers1, {}) == dossiers1

    def test_merge_empty_and_dossiers(self):
        from zam_repondeur.fetch.an.dossiers.models import DossierRef

        dossiers1 = {"a": DossierRef("a", "titre1", "", "", [])}
        assert DossierRef.merge_dossiers({}, dossiers1) == dossiers1

    def test_merge_different_dossiers(self):
        from zam_repondeur.fetch.an.dossiers.models import DossierRef

        dossiers1 = {"a": DossierRef("a", "titre1", "", "", [])}
        dossiers2 = {"b": DossierRef("b", "titre2", "", "", [])}
        assert DossierRef.merge_dossiers(dossiers1, dossiers2) == {
            "a": DossierRef("a", "titre1", "", "", []),
            "b": DossierRef("b", "titre2", "", "", []),
        }

    def test_merge_different_dossiers_reversed(self):
        from zam_repondeur.fetch.an.dossiers.models import DossierRef

        dossiers1 = {"a": DossierRef("a", "titre1", "", "", [])}
        dossiers2 = {"b": DossierRef("b", "titre2", "", "", [])}
        assert DossierRef.merge_dossiers(dossiers2, dossiers1) == {
            "a": DossierRef("a", "titre1", "", "", []),
            "b": DossierRef("b", "titre2", "", "", []),
        }

    def test_merge_identical_dossiers(self):
        from zam_repondeur.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.models.chambre import Chambre

        dossiers1 = {
            "DLR5L15N36030": DossierRef(
                uid="DLR5L15N36030",
                titre="Sécurité sociale : loi de financement 2018",
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/plfss_2018",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/plfss2018.html",
                lectures=[
                    LectureRef(
                        chambre=Chambre.AN,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLANR5L15B0269",
                            type_=TypeTexte.PROJET,
                            chambre=Chambre.AN,
                            legislature=15,
                            numero=269,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 10, 11),
                        ),
                        organe="PO717460",
                    )
                ],
            )
        }
        dossiers2 = deepcopy(dossiers1)
        assert dossiers1 is not dossiers2
        assert dossiers1 == dossiers2

        merged = DossierRef.merge_dossiers(dossiers1, dossiers2)

        assert merged is not dossiers1
        assert merged is not dossiers2
        assert merged == dossiers1
        assert dossiers2 == {}

    def test_merge_dossiers_with_additional_lecture(self):
        from zam_repondeur.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.models.chambre import Chambre

        dossiers1 = {
            "DLR5L15N36030": DossierRef(
                uid="DLR5L15N36030",
                titre="Sécurité sociale : loi de financement 2018",
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/plfss_2018",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/plfss2018.html",
                lectures=[
                    LectureRef(
                        chambre=Chambre.AN,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLANR5L15B0269",
                            type_=TypeTexte.PROJET,
                            chambre=Chambre.AN,
                            legislature=15,
                            numero=269,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 10, 11),
                        ),
                        organe="PO717460",
                    )
                ],
            )
        }
        dossiers2 = {
            "DLR5L15N36030": DossierRef(
                uid="DLR5L15N36030",
                titre="Sécurité sociale : loi de financement 2018",
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/plfss_2018",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/plfss2018.html",
                lectures=[
                    LectureRef(
                        chambre=Chambre.AN,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLANR5L15B0269",
                            type_=TypeTexte.PROJET,
                            chambre=Chambre.AN,
                            legislature=15,
                            numero=269,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 10, 11),
                        ),
                        organe="PO717460",
                    ),
                    LectureRef(
                        chambre=Chambre.SENAT,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLSNR5S299B0063",
                            type_=TypeTexte.PROJET,
                            chambre=Chambre.SENAT,
                            legislature=None,
                            numero=63,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 11, 6),
                        ),
                        organe="PO78718",
                    ),
                ],
            )
        }

        merged = DossierRef.merge_dossiers(dossiers1, dossiers2)

        assert merged == {
            "DLR5L15N36030": DossierRef(
                uid="DLR5L15N36030",
                titre="Sécurité sociale : loi de financement 2018",
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/plfss_2018",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/plfss2018.html",
                lectures=[
                    LectureRef(
                        chambre=Chambre.AN,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLANR5L15B0269",
                            type_=TypeTexte.PROJET,
                            chambre=Chambre.AN,
                            legislature=15,
                            numero=269,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 10, 11),
                        ),
                        organe="PO717460",  # séance publique
                    ),
                    LectureRef(
                        chambre=Chambre.SENAT,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLSNR5S299B0063",
                            type_=TypeTexte.PROJET,
                            chambre=Chambre.SENAT,
                            legislature=None,
                            numero=63,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 11, 6),
                        ),
                        organe="PO78718",  # séance publique
                    ),
                ],
            )
        }


class TestMergeBySenatURL:
    def test_merge_dossiers_by_senat_url_with_additional_lecture(self):
        from zam_repondeur.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.models.chambre import Chambre

        dossiers1 = {
            "DLR5L15N36030": DossierRef(
                uid="DLR5L15N36030",
                titre="Sécurité sociale : loi de financement 2018",
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/plfss_2018",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/plfss2018.html",
                lectures=[
                    LectureRef(
                        chambre=Chambre.AN,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLANR5L15B0269",
                            type_=TypeTexte.PROJET,
                            chambre=Chambre.AN,
                            legislature=15,
                            numero=269,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 10, 11),
                        ),
                        organe="PO717460",
                    )
                ],
            )
        }
        dossiers2 = {
            "ANOTHER": DossierRef(
                uid="ANOTHER",
                titre="Sécurité sociale : loi de financement 2018",
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/plfss_2018",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/plfss2018.html",
                lectures=[
                    LectureRef(
                        chambre=Chambre.AN,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="DIFFERENT",
                            type_=TypeTexte.PROJET,
                            chambre=Chambre.AN,
                            legislature=15,
                            numero=269,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 10, 11),
                        ),
                        organe="PO717460",
                    ),
                    LectureRef(
                        chambre=Chambre.SENAT,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="DIFFERENT2",
                            type_=TypeTexte.PROJET,
                            chambre=Chambre.SENAT,
                            legislature=None,
                            numero=63,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 11, 6),
                        ),
                        organe="PO78718",
                    ),
                ],
            )
        }

        result1, result2 = DossierRef.merge_by("senat_url", dossiers1, dossiers2)

        assert result1 == {
            "DLR5L15N36030": DossierRef(
                uid="DLR5L15N36030",
                titre="Sécurité sociale : loi de financement 2018",
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/plfss_2018",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/plfss2018.html",
                lectures=[
                    LectureRef(
                        chambre=Chambre.AN,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLANR5L15B0269",
                            type_=TypeTexte.PROJET,
                            chambre=Chambre.AN,
                            legislature=15,
                            numero=269,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 10, 11),
                        ),
                        organe="PO717460",
                    ),
                    LectureRef(
                        chambre=Chambre.SENAT,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="DIFFERENT2",
                            type_=TypeTexte.PROJET,
                            chambre=Chambre.SENAT,
                            legislature=None,
                            numero=63,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 11, 6),
                        ),
                        organe="PO78718",
                    ),
                ],
            )
        }
        assert result2 == {}

    def test_merge_dossiers_by_senat_url_more_complex(self):
        from zam_repondeur.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.models.chambre import Chambre

        dossiers1 = {
            "DLR5L15N36030": DossierRef(
                uid="DLR5L15N36030",
                titre="Sécurité sociale : loi de financement 2018",
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/plfss_2018",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/plfss2018.html",
                lectures=[
                    LectureRef(
                        chambre=Chambre.AN,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLANR5L15B0269",
                            type_=TypeTexte.PROJET,
                            chambre=Chambre.AN,
                            legislature=15,
                            numero=269,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 10, 11),
                        ),
                        organe="PO717460",
                    )
                ],
            ),
            "DLR5L15N36159": DossierRef(
                uid="DLR5L15N36159",
                titre="Fonction publique : un Etat au service d'une société de confiance",  # noqa
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/etat_service_societe_confiance",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/pjl17-259.html",
                lectures=[
                    LectureRef(
                        chambre=Chambre.AN,
                        titre="Nouvelle lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLANR5L15B0806",
                            type_=TypeTexte.PROJET,
                            chambre=Chambre.AN,
                            legislature=15,
                            numero=806,
                            titre_long="projet de loi renforçant l'efficacité de l'administration pour une relation de confiance avec le public",  # noqa
                            titre_court="Renforcement de l'efficacité de l'administration pour une relation de confiance avec le public",  # noqa
                            date_depot=date(2018, 3, 21),
                        ),
                        organe="PO744107",  # commission spéciale
                    )
                ],
            ),
        }
        dossiers2 = {
            "OTHER": DossierRef(
                uid="OTHER",
                titre="Sécurité sociale : loi de financement 2018",
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/plfss_2018",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/plfss2018.html",
                lectures=[
                    LectureRef(
                        chambre=Chambre.AN,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="DIFFERENT",
                            type_=TypeTexte.PROJET,
                            chambre=Chambre.AN,
                            legislature=15,
                            numero=269,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 10, 11),
                        ),
                        organe="PO717460",
                    ),
                    LectureRef(
                        chambre=Chambre.SENAT,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="DIFFERENT2",
                            type_=TypeTexte.PROJET,
                            chambre=Chambre.SENAT,
                            legislature=None,
                            numero=63,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 11, 6),
                        ),
                        organe="PO78718",
                    ),
                ],
            ),
            "ANOTHER": DossierRef(
                uid="ANOTHER",
                titre="Sécurité sociale : loi de financement 2019",
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/plfss_2019",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/plfss2019.html",
                lectures=[
                    LectureRef(
                        chambre=Chambre.SENAT,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="DIFFERENT3",
                            type_=TypeTexte.PROJET,
                            chambre=Chambre.SENAT,
                            legislature=None,
                            numero=106,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2019",  # noqa
                            titre_court="PLFSS pour 2019",
                            date_depot=date(2018, 11, 5),
                        ),
                        organe="PO78718",  # séance publique
                    )
                ],
            ),
        }

        result1, result2 = DossierRef.merge_by("senat_url", dossiers1, dossiers2)

        assert result1 == {
            "DLR5L15N36030": DossierRef(
                uid="DLR5L15N36030",
                titre="Sécurité sociale : loi de financement 2018",
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/plfss_2018",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/plfss2018.html",
                lectures=[
                    LectureRef(
                        chambre=Chambre.AN,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLANR5L15B0269",
                            type_=TypeTexte.PROJET,
                            chambre=Chambre.AN,
                            legislature=15,
                            numero=269,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 10, 11),
                        ),
                        organe="PO717460",
                    ),
                    LectureRef(
                        chambre=Chambre.SENAT,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="DIFFERENT2",
                            type_=TypeTexte.PROJET,
                            chambre=Chambre.SENAT,
                            legislature=None,
                            numero=63,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 11, 6),
                        ),
                        organe="PO78718",
                    ),
                ],
            ),
            "DLR5L15N36159": DossierRef(
                uid="DLR5L15N36159",
                titre="Fonction publique : un Etat au service d'une société de confiance",  # noqa
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/etat_service_societe_confiance",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/pjl17-259.html",
                lectures=[
                    LectureRef(
                        chambre=Chambre.AN,
                        titre="Nouvelle lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLANR5L15B0806",
                            type_=TypeTexte.PROJET,
                            chambre=Chambre.AN,
                            legislature=15,
                            numero=806,
                            titre_long="projet de loi renforçant l'efficacité de l'administration pour une relation de confiance avec le public",  # noqa
                            titre_court="Renforcement de l'efficacité de l'administration pour une relation de confiance avec le public",  # noqa
                            date_depot=date(2018, 3, 21),
                        ),
                        organe="PO744107",  # commission spéciale
                    )
                ],
            ),
        }
        assert result2 == {
            "ANOTHER": DossierRef(
                uid="ANOTHER",
                titre="Sécurité sociale : loi de financement 2019",
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/plfss_2019",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/plfss2019.html",
                lectures=[
                    LectureRef(
                        chambre=Chambre.SENAT,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="DIFFERENT3",
                            type_=TypeTexte.PROJET,
                            chambre=Chambre.SENAT,
                            legislature=None,
                            numero=106,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2019",  # noqa
                            titre_court="PLFSS pour 2019",
                            date_depot=date(2018, 11, 5),
                        ),
                        organe="PO78718",  # séance publique
                    )
                ],
            )
        }


class TestAddDossiers:
    def test_senat_commission_lecture(self):
        from zam_repondeur.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )
        from zam_repondeur.models.chambre import Chambre

        dossier_open_data = DossierRef(
            uid="DLR5L15N36030",
            titre="Titre 1",
            an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/plfss_2018",  # noqa
            senat_url="http://www.senat.fr/dossier-legislatif/plfss2018.html",
            lectures=[
                LectureRef(
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Commission saisie au fond",
                    texte=TexteRef(
                        uid="UID-TEXTE-1",
                        type_=TypeTexte.PROJET,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=63,
                        titre_long="",
                        titre_court="",
                        date_depot=date(2017, 11, 6),
                    ),
                    organe="PO211493",  # known exact organe
                ),
                LectureRef(
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="UID-TEXTE-1",
                        type_=TypeTexte.PROJET,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=63,
                        titre_long="",
                        titre_court="",
                        date_depot=date(2017, 11, 6),
                    ),
                    organe="PO78718",
                ),
            ],
        )
        dossier_scraping = DossierRef(
            uid="pjl17-063",
            titre="Titre 2",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/plfss2018.html",
            lectures=[
                LectureRef(
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Commissions",
                    texte=TexteRef(
                        uid="UID-TEXTE-2",
                        type_=TypeTexte.PROJET,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=63,
                        titre_long="",
                        titre_court="",
                        date_depot=date(2017, 11, 6),
                    ),
                    organe="",  # unknown exact organe
                ),
                LectureRef(
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="UID-TEXTE-2",
                        type_=TypeTexte.PROJET,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=63,
                        titre_long="",
                        titre_court="",
                        date_depot=date(2017, 11, 6),
                    ),
                    organe="PO78718",
                ),
            ],
        )

        merged = dossier_open_data + dossier_scraping

        assert merged == DossierRef(
            uid="DLR5L15N36030",
            titre="Titre 1",
            an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/plfss_2018",  # noqa
            senat_url="http://www.senat.fr/dossier-legislatif/plfss2018.html",
            lectures=[
                LectureRef(
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Commission saisie au fond",
                    texte=TexteRef(
                        uid="UID-TEXTE-1",
                        type_=TypeTexte.PROJET,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=63,
                        titre_long="",
                        titre_court="",
                        date_depot=date(2017, 11, 6),
                    ),
                    organe="PO211493",  # known exact organe
                ),
                LectureRef(
                    chambre=Chambre.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="UID-TEXTE-1",
                        type_=TypeTexte.PROJET,
                        chambre=Chambre.SENAT,
                        legislature=None,
                        numero=63,
                        titre_long="",
                        titre_court="",
                        date_depot=date(2017, 11, 6),
                    ),
                    organe="PO78718",
                ),
            ],
        )
