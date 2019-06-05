from copy import deepcopy
from datetime import date


class TestMergeDossiers:
    def test_merge_empty_dossiers(self):
        from zam_repondeur.fetch.an.dossiers.models import DossierRef

        assert DossierRef.merge_dossiers({}, {}) == {}

    def test_merge_dossiers_and_empty(self):
        from zam_repondeur.fetch.an.dossiers.models import DossierRef

        dossiers1 = {"a": DossierRef("a", "titre1", [])}
        assert DossierRef.merge_dossiers(dossiers1, {}) == dossiers1

    def test_merge_empty_and_dossiers(self):
        from zam_repondeur.fetch.an.dossiers.models import DossierRef

        dossiers1 = {"a": DossierRef("a", "titre1", [])}
        assert DossierRef.merge_dossiers({}, dossiers1) == dossiers1

    def test_merge_different_dossiers(self):
        from zam_repondeur.fetch.an.dossiers.models import DossierRef

        dossiers1 = {"a": DossierRef("a", "titre1", [])}
        dossiers2 = {"b": DossierRef("b", "titre2", [])}
        assert DossierRef.merge_dossiers(dossiers1, dossiers2) == {
            "a": DossierRef("a", "titre1", []),
            "b": DossierRef("b", "titre2", []),
        }

    def test_merge_different_dossiers_reversed(self):
        from zam_repondeur.fetch.an.dossiers.models import DossierRef

        dossiers1 = {"a": DossierRef("a", "titre1", [])}
        dossiers2 = {"b": DossierRef("b", "titre2", [])}
        assert DossierRef.merge_dossiers(dossiers2, dossiers1) == {
            "a": DossierRef("a", "titre1", []),
            "b": DossierRef("b", "titre2", []),
        }

    def test_merge_identical_dossiers(self):
        from zam_repondeur.fetch.an.dossiers.models import (
            ChambreRef,
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )

        dossiers1 = {
            "DLR5L15N36030": DossierRef(
                uid="DLR5L15N36030",
                titre="Sécurité sociale : loi de financement 2018",
                lectures=[
                    LectureRef(
                        chambre=ChambreRef.AN,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLANR5L15B0269",
                            type_=TypeTexte.PROJET,
                            chambre=ChambreRef.AN,
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
        assert merged == dossiers1 == dossiers2

    def test_merge_dossiers_with_additional_lecture(self):
        from zam_repondeur.fetch.an.dossiers.models import (
            ChambreRef,
            DossierRef,
            LectureRef,
            TexteRef,
            TypeTexte,
        )

        dossiers1 = {
            "DLR5L15N36030": DossierRef(
                uid="DLR5L15N36030",
                titre="Sécurité sociale : loi de financement 2018",
                lectures=[
                    LectureRef(
                        chambre=ChambreRef.AN,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLANR5L15B0269",
                            type_=TypeTexte.PROJET,
                            chambre=ChambreRef.AN,
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
                lectures=[
                    LectureRef(
                        chambre=ChambreRef.AN,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLANR5L15B0269",
                            type_=TypeTexte.PROJET,
                            chambre=ChambreRef.AN,
                            legislature=15,
                            numero=269,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 10, 11),
                        ),
                        organe="PO717460",
                    ),
                    LectureRef(
                        chambre=ChambreRef.SENAT,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLSNR5S299B0063",
                            type_=TypeTexte.PROJET,
                            chambre=ChambreRef.SENAT,
                            legislature=2017,
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
                lectures=[
                    LectureRef(
                        chambre=ChambreRef.AN,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLANR5L15B0269",
                            type_=TypeTexte.PROJET,
                            chambre=ChambreRef.AN,
                            legislature=15,
                            numero=269,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 10, 11),
                        ),
                        organe="PO717460",  # séance publique
                    ),
                    LectureRef(
                        chambre=ChambreRef.SENAT,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLSNR5S299B0063",
                            type_=TypeTexte.PROJET,
                            chambre=ChambreRef.SENAT,
                            legislature=2017,
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
